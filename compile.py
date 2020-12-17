# windows: python compile.py bdist_msi
# IEXPRESS /N D:\Benutzer\haschtl\Dokumente\GIT\kellerlogger\build\RTOC_v2.SED


from cx_Freeze import setup, Executable, __version__ as cx_version
import os
import sys
import time

print(cx_version)
time.sleep(2)
# os.environ['TCL_LIBRARY'] = r'C:\Users\hasch\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Users\hasch\AppData\Local\Programs\Python\Python36\tcl\tk8.6'
buildOptions = dict(
    packages=["tkinter", "win10toast", "pystray",
              "PIL", "xml", "yaml", "json", "clr", "os", "sys", "threading", "time"],
    # excludes=["scipy.spatial.cKDTree"], 
    # includes=["RTOC/", "RTOC/LoggerPlugin", "RTOC/RTLogger/scriptLibrary"], 
    include_files=["README.md", "OpenHardwareMonitorLib.dll", "icon.ico", "config.yaml"
                   ]
                   )

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    # base)#, icon="data/icon.png",shortcutName="RealTimeOpenControl",shortcutDir="MyProgramMenu")
    Executable('ModernFanControl.py', base=None, icon="icon.ico")
]

setup(
    name='ModernFanControl',
    version='1.0',
    description='ModernFanControl',
    options=dict(build_exe=buildOptions),
    executables=executables
)
