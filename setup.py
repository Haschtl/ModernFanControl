from cx_Freeze import setup, Executable
import sys
buildOptions = dict(
    packages=["clr", "platform"]
)

base = 'Win64GUI' if sys.platform == 'win64' else None

executables = [
    Executable('test.py', base=None, icon="icon.ico")
]

setup(
    name='Test',
    version='1.0',
    description='Test',
    options=dict(build_exe=buildOptions),
    executables=executables
)
