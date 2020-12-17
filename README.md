
# Modern Fan Control
This is a custom fan-control GUI based on [NoteBook FanControl](https://github.com/hirschmann/nbfc)

NoteBook FanControl provides configurations for many notebooks. This tool can load these configuration files. **Note that this tool uses only a subset of the functions of NoteBook FanControl**. Nevertheless it also offers some extra features - and it is a good starting point, if you want to make very custom fan control.

This project is primarily made for a **HP Spectre 15-df1015ng** as it contains a workaround, which makes controlling the fan possible (seems to be some rubbish thermalzone implementation from HP).
The problem is, that you cannot set a value below a certain threshold, if the fan was off before (e.g. you can't set the fan speed from 0 to 10%, but you can set it from 100% to 10%). This causes the fan to only work after a certain threshold (around 50%) - **This is the default behaviour of the Spectre (WTF?!)**

## Features (just like NoteBook FanControl)
- Tool runs in systemtray only
- You can load different config-files
- You can enable Auto-Mode or control the fan-speed manually
- You can view the desired and actual fan-speed value
- You can quickly edit a config-file and simply reload it without restarting the tool

## Extra features:
- FanStartThreshold and FanStartDelay added in configuration files:
  ```
  <FanControlConfigV2>
  <FanConfigurations>
    <FanConfiguration>
	<FanStartThreshold>100</FanStartThreshold>
	<FanStartThresholdDelay>2500</FanStartThresholdDelay>
    ...
  ```
  This configuration will set the fan to 100% for 2500ms, if the desired fan-speed is below 100%.
- Define a hotkey to quickly show/hide the GUI


## Setup
This tool is based on python3. 
1. Install the dependencies

### Dependencies
- Python3
- NoteBook FanControl installed
- Configuration available for your notebook
- Python modules: `pip install tkinter win10toast pystray PIL xml yaml json clr`

2. Clone this repo to `C:/ModernFanControl` (Note: You may change the directory, but it **must** be on the same drive as your operating system)
3. Check the config-file in `C:/ModernFanControl/config.yaml`. The `nbfc-path` entry must point to the directory, where NoteBook FanControl is installed (it will need the `ec-probe.exe`).
4. Start the tool with the `run.bat`-file
5. (Optional) Create a windows task to run the tool on login: Open the windows task tool and import the `ModernFanControlWindowsTask.xml` task.


# Credits
Many thanks to the developers of NoteBook FanControl and OpenHardwareMonitor making this project possible


# Known Issues:
- If an error occurs saying, that the OpenHardwareMonitorLib.dll could not be found, execute `streams.exe -d ../OpenHardwareMonitorLib.dll`
- This project must be on the same drive as windows (default C:/)
