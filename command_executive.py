"""Uses pyautogui to open the command prompt and start the streamlit application."""

import os
import pyautogui
import pyperclip
import time


pyautogui.moveTo(600, 1042)
pyautogui.click()
pyautogui.typewrite('cmd')
pyautogui.press('enter')
time.sleep(1)
pyautogui.typewrite('cd C:\\Users\\rjc52\\PycharmProjects\\TimelineProject\\Timeline_Project')
pyautogui.press('enter')
pyautogui.write('streamlit run ')
pyperclip.copy('📁')
pyautogui.hotkey('ctrl', 'v')
pyautogui.write('_Upload_Files.py')
pyautogui.press('enter')
