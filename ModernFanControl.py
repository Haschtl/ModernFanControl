import yaml
import sys
import threading
import time
import os
import traceback

from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
from win10toast import ToastNotifier
import pystray
from PIL import Image, ImageDraw, ImageFont
import keyboard

from HardwareMonitor import HWMonitor
from XmlDictConfig import load_xml_config
from ecprobe import ECProbe

APPNAME = "Modern Fan Control"
BACKGROUND_COLOR = "black"
SLIDER_BACKGROUND_COLOR = "#303030"
FOREGROUND_COLOR = "white"
SLIDER_COLOR = "white"
WIDTH = 150
HEIGHT = 190 #+20
WIN_TASKBAR_HEIGHT = 40  # +30+1
WINDOW_RIGHT_MARGIN = 200

def load_config():
    config = {}
    with open("./config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(-1)
    if "nbfc-path" not in config.keys():
        print("No 'nbfc-path' provided in the config.yaml.")
        sys.exit(-1)
    if "config-paths" not in config.keys():
        print("No 'config-paths' provided in the config.yaml.")
        sys.exit(-1)
    return config

class ModernFanControl():
    def __init__(self):
        self.read_lut = None
        self.write_lut = None
        self.show_raw = False
        self.visible = True
        self.last_write_value = -1
        self.init_configurations()
        self.load_configuration(0)
        self.init_hotkey()
        self.probe = ECProbe(self.nbfc_path)
        self.hw = HWMonitor(cpu=True)
        self._job = None
        self.cur_fan_speed = 0
        self.windows = self.init_window()
        self.toaster = ToastNotifier()

    def run(self):
        self.build()
        self.run_thread()
        if self.visible is False:
            self.hide_window()
        self.window.mainloop()
        # keyboard.wait('esc')

    def init_window(self):
        self.window = tk.Tk()
        self.window.title(APPNAME)
        self.window.configure(bg=BACKGROUND_COLOR)
        self.style = ttk.Style(self.window)
        self.window.iconbitmap('./icon.ico')
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(1)
        self.window.resizable(False, False)
        self.window.update()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(get_geometry(
            WIDTH, HEIGHT, screen_width, screen_height))

    def init_systemtray(self):
        menu = pystray.Menu(
            pystray.MenuItem(text="Show Main Window",
                             action=self.toggle_window, default=True, visible=False),
            pystray.MenuItem('Quit', self.quit_window),
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Hide', self.hide_window),
            pystray.MenuItem('Toggle raw data', self.toggle_raw),
            pystray.MenuItem('Edit config', self.edit_config)
        )
        self.systemtray = pystray.Icon(
            "name", self.create_systray_image(), APPNAME, menu)
        self.systemtray.run()

    def init_hotkey(self):
        keyboard.add_hotkey(self.hotkey.lower(), self.execute_hotkey)


    def execute_hotkey(self):
        # print(self.hotkey.lower())
        self.toggle_window()

    def on_hotkey_press(self, key):
        if any([key in COMBO for COMBO in self.hotkey_combinations]):
            self.current_pressed_key.add(key)
            if any(all(k in self.current_pressed_key for k in COMBO) for COMBO in self.hotkey_combinations):
                self.execute_hotkey()

    def on_hotkey_release(self, key):
        if any([key in COMBO for COMBO in self.hotkey_combinations]):
            self.current_pressed_key.remove(key)

    def init_configurations(self):
        config = load_config()
        self.nbfc_path = config["nbfc-path"]
        self.config_paths = config["config-paths"]
        self.visible = not config["minimized"]
        self.hotkey = config["hotkey"]
        self._configs = []
        for cp in self.config_paths:
            cp = os.path.abspath(cp)
            if os.path.isdir(cp):
                files = os.listdir(cp)
                for file in files:
                    self._tryload_config(os.path.join(cp, file))
            else:
                self._tryload_config(cp)

    def _tryload_config(self, path):
        if path.endswith(".xml"):
            try:
                config = load_xml_config(path)
                config["file"] = path
                self._configs.append(config)
            except Exception as e:
                print(e)

    def build(self):
        frame = tk.Frame(master=self.window, relief=tk.FLAT, borderwidth=5, bg=BACKGROUND_COLOR)
        frame.pack(side=tk.TOP)
        self.temp_label = tk.Label(master=frame, text="", bg=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
        self.temp_label.pack()

        choices = [config["NotebookModel"] for config in self._configs]
        self.selected_notebook_model = tk.StringVar()
        self.selected_notebook_model.set(choices[0])
        self.selected_notebook_model.trace('w', self.change_selection)
        self.config_selector = tk.OptionMenu(
            self.window, self.selected_notebook_model, *choices)
        self.config_selector.config(bg=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, highlightbackground=BACKGROUND_COLOR,
                                   activebackground=BACKGROUND_COLOR, activeforeground=FOREGROUND_COLOR)
        self.config_selector["menu"].config(
            bg=SLIDER_BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, activeforeground=FOREGROUND_COLOR, foreground=FOREGROUND_COLOR)
        self.config_selector["highlightthickness"] = 0
        self.config_selector["menu"]["borderwidth"] = 0
        self.config_selector.pack()

        self.enabled = tk.IntVar(value=1)

        self.desired_fan_speed = tk.Scale(
            self.window, label="Soll", from_=0, to=100, highlightbackground=BACKGROUND_COLOR, borderwidth=0, orient=tk.HORIZONTAL, command=self.desired_slider_changed, bg=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, troughcolor=SLIDER_BACKGROUND_COLOR, activebackground=SLIDER_COLOR, sliderrelief='flat')
        self.desired_fan_speed.pack()
        self.actual_fan_speed = tk.Scale(self.window, label="Ist", highlightbackground=BACKGROUND_COLOR, borderwidth=0, from_=0, to=100, orient=tk.HORIZONTAL, state=tk.DISABLED, bg=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, troughcolor=SLIDER_BACKGROUND_COLOR, activebackground=SLIDER_COLOR, sliderrelief='flat')
        self.actual_fan_speed.pack()

        self.auto = tk.IntVar(value=1)

        self.auto_checkbox = tk.Checkbutton(self.window, text='Auto', variable=self.auto, onvalue=1, offvalue=0, command=self.toggle_auto, bg=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, selectcolor=BACKGROUND_COLOR)
        self.auto_checkbox.pack()

        threading.Thread(target=self.init_systemtray).start()
        
    def select_configuration(self, name_or_idx):
        cfg_idx = 0
        if type(name_or_idx) == str:
            for idx, config in enumerate(self._configs):
                if config["NotebookModel"] == name_or_idx:
                    cfg_idx = idx
                    break
        else:
            cfg_idx = name_or_idx
        return self._configs[cfg_idx]

    def load_configuration(self,name):
        selected_config = self.select_configuration(name)
        self.load_fan_configuration(selected_config["FanConfigurations"]["FanConfiguration"])
        self.config.update({
            "file": load_dictkey(selected_config, "file", "", str),
            "ecPollInterval": load_dictkey(selected_config, "EcPollInterval", 3000, float),
            "criticalTemperature": load_dictkey(selected_config, "CriticalTemperature", 95, float),
            "readWriteWords": load_dictkey(selected_config, "ReadWriteWords", False, bool),
            "author": load_dictkey(selected_config, "Author", "", str),
            "notebookModel": load_dictkey(selected_config, "NotebookModel", "", str),
        })
        return self.print_configuration()

    def load_fan_configuration(self, fan_config):    
        self.temp_thresholds = fan_config["TemperatureThresholds"]["TemperatureThreshold"]

        write_register = fan_config["WriteRegister"]
        read_register = fan_config["ReadRegister"]
        min_speed_value = load_dictkey(fan_config, "MinSpeedValue", 0, int)
        max_speed_value = load_dictkey(fan_config, "MaxSpeedValue", 100, int)

        min_speed_value_read = load_dictkey(fan_config, "MinSpeedValueRead", min_speed_value, int)
        max_speed_value_read = load_dictkey(fan_config, "MaxSpeedValueRead", max_speed_value, int)

        fan_start_threshold = load_dictkey(fan_config, "FanStartThreshold", None, int)
        fan_start_threshold_delay = load_dictkey(fan_config, "FanStartThresholdDelay", 200, int)
        independent_read_min_max_values = load_dictkey(fan_config, "IndependentReadMinMaxValues", False, bool)
        reset_required = load_dictkey(fan_config, "ResetRequired", False, bool)
        fan_speed_reset_value = load_dictkey(fan_config, "FanSpeedResetValue", 0, int)
        fan_display_name = load_dictkey(fan_config, "FanDisplayName", False, str)
        
        self.config = {
            "writeRegister": write_register,
            "readRegister": read_register,
            "minSpeedValueRead": min_speed_value_read,
            "maxSpeedValueRead": max_speed_value_read,
            "minSpeedValue": min_speed_value,
            "maxSpeedValue": max_speed_value,
            "fanStartThreshold": fan_start_threshold,
            "fanStartThresholdDelay": fan_start_threshold_delay,
            "independentReadMinMaxValues": independent_read_min_max_values,
            "resetRequired": reset_required,
            "fanSpeedResetValue": fan_speed_reset_value,
            "fanDisplayName": fan_display_name,
        }
        self.cur_threshold = None

        if "FanSpeedPercentageOverrides" in fan_config.keys():
            self.create_fan_lut(fan_config["FanSpeedPercentageOverrides"]["FanSpeedPercentageOverride"])
        else:
            self.read_lut = None
            self.write_lut = None

    def create_fan_lut(self, overrides):
        write_keypoints = {0: self.config["minSpeedValue"]}
        read_keypoints = {self.config["minSpeedValue"]:0}
        for override in overrides:
            op = load_dictkey(override, "TargetOperation", None, str)
            fanspeed = load_dictkey(override, "FanSpeedValue", None, int)
            fanpercent = load_dictkey(override, "FanSpeedPercentage", None, int)
            if fanspeed is None or fanpercent is None:
                continue
            if op == "Write" or op == None:
                write_keypoints[fanpercent] = fanspeed
            if op == "Read" or op == None:
                read_keypoints[fanspeed] = fanpercent

        write_keypoints[100] = self.config["maxSpeedValue"]
        read_keypoints[self.config["maxSpeedValue"]] = 100
        
        if len(read_keypoints.keys()) > 0:
            self.read_lut = read_keypoints
        else:
            self.read_lut = None
        if len(write_keypoints.keys()) > 0:
            self.write_lut = write_keypoints
        else:
            self.write_lut = None
        # print(self.read_lut)
        # print(self.write_lut)

    def read_value_to_percentage(self, value):
        if self.config["independentReadMinMaxValues"]:
            minvalue = self.config["minSpeedValueRead"]
            maxvalue = self.config["maxSpeedValueRead"]
        else:
            minvalue = self.config["minSpeedValue"]
            maxvalue = self.config["maxSpeedValue"]

        if value < minvalue:
            value = minvalue
        elif value > maxvalue:
            value = maxvalue

        if self.read_lut is None:
            return (value-minvalue)/(maxvalue-minvalue)*100
        else:
            read_value = self.read_from_lut(self.read_lut, value)
            return read_value

    def percentage_to_write_value(self, percentage):
        minvalue = self.config["minSpeedValue"]
        maxvalue = self.config["maxSpeedValue"]
        if self.write_lut is None:
            percentage = float(percentage)
            return int(percentage/100*(maxvalue-minvalue) + minvalue)
        else:
            write_value = self.read_from_lut(self.write_lut, percentage)
            return write_value 

    def read_from_lut(self, lut, value):
        last_out_value = None
        last_in_value = None
        for keypoint in lut.keys():
            if value <= keypoint and last_out_value is not None:
                offset = last_out_value
                din = keypoint-last_in_value
                dout = lut[keypoint]-last_out_value
                write_value = int(offset + dout/din*(value-last_in_value))
                return write_value 
            last_out_value = lut[keypoint]
            last_in_value = keypoint
        print("out of lut range!")
        return None


    def print_configuration(self):
        info_str = ""
        try:
            for threshold in self.temp_thresholds:
                lower = float(threshold["DownThreshold"])
                upper = float(threshold["UpThreshold"])
                value = threshold["FanSpeed"]
                info_str += "{}°C -> {}°C: {}%\n".format(lower, upper, value)
        except Exception:
            lower = float(self.temp_thresholds["DownThreshold"])
            upper = float(self.temp_thresholds["UpThreshold"])
            value = self.temp_thresholds["FanSpeed"]
            info_str += "{}°C -> {}°C: {}%\n".format(lower, upper, value)
            self.temp_thresholds = [self.temp_thresholds]
        info_str += """
Fan: {name}
Author: {author}
Write register: {write}
Read register: {read}
speed range (read): {sprmin} -> {sprmax} (Enabled: {ind})
speed range: {spmin} -> {spmax}
Fan start threshold: {fant}% (Delay: {fantd}s)
Poll interval: {poll}s
Reset: Enabled: {reset}, Value: {resetv} (not supported)
Critical temperature: {critic}°C
ReadWriteWords: {words} (not supported)
        """.format(write=self.config["writeRegister"], 
                   read=self.config["readRegister"],
                   sprmin=self.config["minSpeedValueRead"],
                   sprmax=self.config["maxSpeedValueRead"],
                   spmin=self.config["minSpeedValue"],
                   spmax=self.config["maxSpeedValue"],
                   fant=self.config["fanStartThreshold"],
                   fantd=self.config["fanStartThresholdDelay"],
                   poll=self.config["ecPollInterval"]/1000,
                   ind=self.config["independentReadMinMaxValues"],
                   reset=self.config["resetRequired"],
                   resetv=self.config["fanSpeedResetValue"],
                   name=self.config["fanDisplayName"],
                   author=self.config["author"],
                   critic=self.config["criticalTemperature"],
                   words=self.config["readWriteWords"],
        )
        return info_str

    def update_configurations(self):
        self.init_configurations()
        self.auto.set(0)
        menu = self.config_selector["menu"]
        menu.delete(0, "end")
        choices = [config["NotebookModel"] for config in self._configs]
        for string in choices:
            menu.add_command(
                label=string, command=lambda value=string: self.selected_notebook_model.set(value))

    def edit_config(self):
        file = self.config["file"]
        os.system('"'+file+'"')

    def stop_thread(self):
        self.thread_running = False

    def run_thread(self):
        self.thread_running = True
        self.thread = threading.Thread(target=self.monitor_temp)
        self.thread.start()

    def change_selection(self, *args):
        msg = self.load_configuration(self.selected_notebook_model.get())
        messagebox.showinfo(title="Configuration loaded", message=msg)
        self.update_configurations()

    def toggle_auto(self):
        if (self.auto.get() == 1):
            self.desired_fan_speed.config(state=tk.DISABLED)
        else:
            self.desired_fan_speed.config(state=tk.NORMAL)
        # pass

    def toggle_raw(self):
        self.show_raw = not self.show_raw


    def monitor_temp(self):
        # self.show_toast(APPNAME+" started")
        while self.thread_running:
            try:
                data = self.hw.read()
                self.temp_label.config(text="{}°C".format(data["sensor"]))
                self.systemtray.icon = self.create_systray_image(
                    int(data["sensor"]))
                fan_speed = self.get_fan_speed()
                self.cur_fan_speed = fan_speed["percentage"]
                if self.cur_fan_speed<=100 and self.cur_fan_speed>=0:
                    self.actual_fan_speed.config(state=tk.NORMAL)
                    self.actual_fan_speed.set(self.cur_fan_speed)
                    self.actual_fan_speed.config(state=tk.DISABLED)
                    if self.auto.get() == 1:
                        written_value = self.control_temperature(data)
                        if self.show_raw:
                            self.temp_label.config(text="{}°C (w:{} r:{})".format(data["sensor"], written_value, fan_speed["value"]))
                if self.show_raw:
                    self.temp_label.config(text="{}°C (r:{})".format(data["sensor"], fan_speed["value"]))
            except Exception as e:
                print(traceback.format_exc())
                print(e)
            time.sleep(self.config["ecPollInterval"]/1000)

    def control_temperature(self, data):
        if self.enabled.get() == 1:
            cur_temp = data["sensor"]
            thresholds = self.temp_thresholds
            cur_threshold = self.cur_threshold
            if cur_temp > self.config["criticalTemperature"]:
                written_value = self.set_fan_speed(self.config["maxSpeedValue"])
                return written_value
            if cur_threshold is not None and cur_temp > float(cur_threshold["DownThreshold"]) and cur_temp < float(cur_threshold["UpThreshold"]) and self.enabled.get() == 1:
                written_value = self.set_fan_speed(cur_threshold["FanSpeed"])
                return written_value
            for threshold in thresholds:
                if cur_temp > float(threshold["DownThreshold"]) and cur_temp < float(threshold["UpThreshold"]) and self.enabled.get() == 1:
                    written_value = self.set_fan_speed(threshold["FanSpeed"])
                    self.cur_threshold = threshold
                    return written_value
            return None
        # print("a loop without controlling happend")

    def get_fan_speed(self):
        decvalue = self.probe.read(self.config["readRegister"])
        percentage = self.read_value_to_percentage(decvalue)
        # print("Get: {}, {}".format(decvalue, percentage))
        return {"percentage": int(percentage), "value":int(decvalue)}
            
    def desired_slider_changed(self, value):
        if self._job:
            self.window.after_cancel(self._job)
        # self.auto.set(0)
        self._job = self.window.after(500, self._set_fan_speed)

    def _set_fan_speed(self):
        value = int(self.desired_fan_speed.get())
        if self.enabled.get() == 1:
            self.set_fan_speed(value, update_gui=False)

    def set_fan_speed(self, value, update_gui=True):
        nolimit = True
        force_set = False
        value = float(value)
        is_different_to_last_write = self.last_write_value != value
        differs_from_current = abs(self.cur_fan_speed-value)>5
        if is_different_to_last_write or force_set or differs_from_current:
            if value!=0 and self.config["fanStartThreshold"] is not None and (self.cur_fan_speed==0 or nolimit):
                threshold = self.config["fanStartThreshold"]
                if float(value) < threshold:
                    self.write_fan_speed(threshold)
                    time.sleep(self.config["fanStartThresholdDelay"]/1000)
            written_value = self.write_fan_speed(value)
            self.last_write_value = value
            if update_gui:
                self.desired_fan_speed.config(state=tk.NORMAL)
                self.desired_fan_speed.set(value)
                self.desired_fan_speed.config(state=tk.DISABLED)
                # self.auto.set(1)
            return written_value
    
    def write_fan_speed(self, value):
        register = self.config["writeRegister"]
        write_value = self.percentage_to_write_value(value)
        # print("Set: {}, {}".format(write_value, value))
        self.probe.write(register, write_value)
        return write_value

    def show_toast(self, msg):
        def _show(toaster, msg):
            toaster.show_toast(APPNAME, msg)
        
        a = threading.Thread(target=_show, args=[self.toaster, msg])
        a.start()

    def quit_window(self):
        self.stop_thread()
        self.systemtray.stop()
        self.window.after(0, self.window.destroy)

    def show_window(self):
        self.visible = True
        self.window.after(0, self.window.deiconify)

    def hide_window(self):
        self.visible = False
        self.window.withdraw()

    def toggle_window(self):
        if self.visible:
            self.hide_window()
        else:
            self.show_window()

    def create_systray_image(self, text="--", width=60, height=30):
        # Generate an image and draw a pattern
        image = Image.new('RGBA', (width, height), "#00000000")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", int(height*0.8))  
        draw.text((0, 0), str(text)+"°C", font = font, align ="left")  
        return image


def get_geometry(w=300, h=200, screen_width=1920, screen_height=1080):
    taskbar_height = WIN_TASKBAR_HEIGHT 
    right_margin = WINDOW_RIGHT_MARGIN
    x = (screen_width - w)
    y = (screen_height-h)
    y = y-taskbar_height
    x = x-right_margin
    return '%dx%d+%d+%d' % (w, h, x, y)

def load_dictkey(dict, key, alt=None, desired_type=int):
        if key in dict.keys():
            return desired_type(dict[key])
        else:
            return alt

if __name__ == "__main__":
    mfc = ModernFanControl()
    mfc.run()
