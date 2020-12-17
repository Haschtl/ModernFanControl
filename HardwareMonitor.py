import clr  # package pythonnet, not clr
# import os
# import math


openhardwaremonitor_hwtypes = ['Mainboard', 'SuperIO', 'CPU',
    'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD']
cputhermometer_hwtypes = ['Mainboard', 'SuperIO', 'CPU',
    'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD']
openhardwaremonitor_sensortypes = ['Voltage', 'Clock', 'Temperature', 'Load',
    'Fan', 'Flow', 'Control', 'Level', 'Factor', 'Power', 'Data', 'SmallData']
cputhermometer_sensortypes = [
    'Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level']

class HWMonitor():
    def __init__(self, cpu=False, mainboard=False, ram=False, gpu=False, hdd=False):
        self._ = initialize_openhardwaremonitor(
            cpu=cpu, mainboard=mainboard, ram=ram, gpu=gpu, hdd=hdd)

    def read(self):
        if self._ is not None:
            return fetch_stats(self._)
        else:
            return None


def initialize_openhardwaremonitor(cpu=False,mainboard=False,ram=False,gpu=False,hdd=False):
    # import clr  # package pythonnet, not clr
    file = 'OpenHardwareMonitorLib'
    # file = os.path.join(os.curdir,file)
    try:
        clr.AddReference(file)

        from OpenHardwareMonitor import Hardware

        handle = Hardware.Computer()
        handle.MainboardEnabled = mainboard
        handle.CPUEnabled = cpu
        handle.RAMEnabled = ram
        handle.GPUEnabled = gpu
        handle.HDDEnabled = hdd
        handle.Open()
        return handle
    except Exception:
        return None


def initialize_cputhermometer():
    file = 'CPUThermometerLib.dll'
    clr.AddReference(file)

    from CPUThermometer import Hardware
    handle = Hardware.Computer()
    handle.CPUEnabled = True
    handle.Open()
    return handle


def fetch_stats(handle):
    sensor_data = {}
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            sensor_data.update(parse_sensor(sensor))
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                sensor_data.update(parse_sensor(subsensor))
    all_values = sensor_data.values()
    if len(all_values)>0:
        mean = sum(all_values)/len(all_values)
    else:
        mean = -1
    if "CPU Package" in sensor_data.keys():
        sensor_data["sensor"] = sensor_data["CPU Package"]
    else:
        sensor_data["sensor"] = -1
    sensor_data["mean"] = mean
    return sensor_data
    
def parse_sensor(sensor):
    if sensor.Value is not None:
        if type(sensor).__module__ == 'CPUThermometer.Hardware':
            sensortypes = cputhermometer_sensortypes
            # hardwaretypes = cputhermometer_hwtypes
        elif type(sensor).__module__ == 'OpenHardwareMonitor.Hardware':
            sensortypes = openhardwaremonitor_sensortypes
            # hardwaretypes = openhardwaremonitor_hwtypes
        else:
            return {}

        if sensor.SensorType == sensortypes.index('Temperature'):
            # print(u"%s %s Temperature Sensor #%i %s - %s\u00B0C" %
            #         (hardwaretypes[sensor.Hardware.HardwareType], sensor.Hardware.Name, sensor.Index, sensor.Name, sensor.Value))
            return {sensor.Name: sensor.Value}
    return {}


if __name__ == "__main__":
    print("OpenHardwareMonitor:")
    HardwareHandle = initialize_openhardwaremonitor(cpu=True)
    data = fetch_stats(HardwareHandle)
    print(data)
    # print("\nCPUMonitor:")
    # CPUHandle = initialize_cputhermometer()
    # fetch_stats(CPUHandle)
