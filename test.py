#!/usr/bin/python3

"""Switch to browser and refresh"""

import pyautogui

# Switch to browser
pyautogui.hotkey('alt', 'h')
# Refresh browser
pyautogui.typewrite(['f5'], interval=0.25)
