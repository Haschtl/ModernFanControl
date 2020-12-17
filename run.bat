Rem CONSOLESTATE /Hide
Rem SETCONSOLE /minimize
Rem TITLE HideMePlease
Rem FOR /F %%A IN ('CMDOW ˆ| FIND "HideMePlease"') DO CMDOW %%A /HID
python ModernFanControl.py