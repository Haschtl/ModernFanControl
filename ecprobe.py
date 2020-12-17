import subprocess
import os

class ECProbe():
    def __init__(self, path):
        self.path = path
        self.executable = os.path.join(self.path, "ec-probe.exe")

    def read(self, register):
        try:
            out = subprocess.Popen([self.executable, 'read', str(register)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
            stdout, stderr = out.communicate()
            value = int(stdout.decode("utf-8").split(" ")[0])
            # print(value)
            return value
        except Exception as e:
            print(e)
            return None

    def write(self, register, value):
        # print(value)
        try:
            out = subprocess.Popen([self.executable, 'write', str(register), str(value)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            # stdout, stderr = out.communicate()
            # # value = int(stdout.decode("utf-8").split(" ")[0])
            # print(stdout)
            # return value
        except Exception as e:
            print(e)
            # return None


if __name__ == "__main__":
    import time

    probe = ECProbe("C:\\Program Files (x86)\\NoteBook FanControl")
    print(probe.read(0x58))

    probe.write(0xF4,0x60)

    print(probe.read(0x58))
    time.sleep(8)
    print(probe.read(0x58))

    probe.write(0xF4, 0x00)

    print(probe.read(0x58))
    time.sleep(8)
    print(probe.read(0x58))
