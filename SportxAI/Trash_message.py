import pytesseract
from PIL import ImageGrab
import pyautogui

# 截取屏幕
screenshot = ImageGrab.grab()

# 使用Tesseract进行文字检测和识别
data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

# 假设我们要点击的文字是"Click Me"
target_text = "Click Me"

# 遍历检测到的文字
for i in range(len(data['text'])):
    if data['text'][i] == target_text:
        # 获取文字位置
        x = data['left'][i]
        y = data['top'][i]
        width = data['width'][i]
        height = data['height'][i]
        
        # 计算中心点
        center_x = x + width // 2
        center_y = y + height // 2
        
        # 点击中心点
        pyautogui.click(center_x, center_y)
        break

print(data['text'])  # 列印所有識別到的文字
print("Finished")