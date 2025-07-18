import time
import subprocess
import re
import sys
import chardet
import os
import pyperclip
import io

def extract_registration(text):
    # 捕捉 print 輸出
    output_capture = io.StringIO()  # 建立 StringIO 物件
    sys.stdout = output_capture  # 將 stdout 重定向到 StringIO
    #sys.stdout = open(r"C:\Users\kevin\Downloads\clipboard.txt",'w',encoding='utf-8')
# 定義包含「場館資訊」和「時段及成員資訊」的完整區塊
# 正則表達式會在日期出現時匹配到下一個日期或文本結尾
    full_section_pattern = r'❣️.*?❣️.*?.(?=❣️.*?❣️.*?.|\Z)'
    # 查找所有符合的完整區塊，然後取最後一個
    sections = re.findall(full_section_pattern, text, re.DOTALL)
    if sections:    
        # 取出最後一個完整區塊
        last_section = sections[-1]

        info_section = re.search(r'❣️.*?❣️.*?.*?\n——————————————',last_section,re.DOTALL)
        print(info_section.group())
        # 定義時段資訊的正則表達式
        session_pattern = r'([A-Za-z])\.?時段\s?\(?(\d{2}:\d{2})\~?\-?(\d{2}:\d{2})\)?(.*?)(?=[A-Za-z]\.?時段\s?|\Z)'
        # 提取每個時段的時間範圍及成員名單
        sessions = re.findall(session_pattern, last_section,re.DOTALL)
        if sessions:
            sessions_str = re.findall(r'[A-Za-z]\.?時段\s?\(?\d{2}:\d{2}\~?\-?\d{2}:\d{2}\)?.*?(?=[A-Za-z]\.?時段\s?|\Z)', last_section,re.DOTALL)
            for session,session_str in zip(sessions,sessions_str):
                session_info = re.search(r'[A-Za-z]\.?時段.*?(?=\n1\.)',session_str,re.DOTALL)
                print(session_info.group())
                time_slot = session[0] # 時段標記    
                start_time = session[1] # 開始時間
                end_time = session[2]   # 結束時間
                members = session[3].strip().splitlines()  # 成員名單
                # 使用正則表達式篩選以數字開頭的成員條目，並提取數字以便排序
                member_list = []
                for member in members:
                    member = member.strip()
                    match = re.match(r'^(\d{1,2})\.(.*)(\s\d{1,2})?', member)
                    if match:
                        number = int(match.group(1))  # 提取開頭數字
                        name = match.group(2).strip()  # 提取成員名稱
                        if name != "":
                            member_list.append(name)  # 添加到成員列表中
                #用戶報名訊息
                client_register_message_pattern = r'\d{1,2}:\d{2}\s([\u4e00-\u9fffA-Za-z]+)\s([A-Za-z])([+\-加減])(\d{1,2})\s?([\u4e00-\u9fffA-Za-z]+)?'
                client_register_messages = re.findall(client_register_message_pattern, last_section, flags=re.DOTALL)
                if client_register_messages:
                    client_register_name_list = []
                    for client_register_message in client_register_messages:
                        if client_register_message[4]:
                            client_register_name = client_register_message[4]
                        else:
                            client_register_name = client_register_message[0]
                        client_register_session = client_register_message[1]
                        client_register_in_out = client_register_message[2] 
                        client_register_in_out_times = int(client_register_message[3])
                        client_register_name_other = client_register_message[4]
                        if client_register_session == time_slot:
                            if client_register_in_out == "+":
                                for i in range(client_register_in_out_times):        
                                    member_list.append(client_register_name)
                            elif client_register_in_out == "-":
                                for i in range(client_register_in_out_times):
                                    if client_register_name in member_list:        
                                        member_list.remove(client_register_name)
            
                index = 0
                for index, name in enumerate(member_list, start=1):
                    print(f"{index}.{name}")
                while index < 2:
                    index+=1
                    print(f"{index}.")
                if index == 22:
                    print(f"{index+1}.\n24.")
                if index < 23:
                    print(f"{index+1}.\n…\n24.")
                elif index == 23:print("24.")
                print("——————————————")
        else:
            print("未找到成員資訊中的時段和成員名單")
    else:
        print("未找到包含場館資訊和時段及成員資訊的完整區塊")
    clipboard.new_output_message = output_capture.getvalue()
    # 還原 sys.stdout
    sys.stdout = sys.__stdout__

    
def copy_file_content_to_clipboard(file_path):
    # 讀取文件內容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 將內容複製到剪貼簿
    pyperclip.copy(content)

def convert_utf8_to_utf16(input_file_path, output_file_path):
    try:
        # 以 UTF-8 編碼讀取文件
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            content = input_file.read()  # 讀取內容

        # 以 UTF-16 編碼寫入文件
        with open(output_file_path, 'w', encoding='utf-16') as output_file:
            output_file.write(content)  # 寫入內容

        print(f"成功將 {input_file_path} 轉換為 {output_file_path}。")
    except Exception as e:
        print(f"轉換過程中發生錯誤: {e}")


if __name__ == "__main__":
    class clipboard:
        new_output_message = ""
        temp_output_message = ""
    class input_message:
        new_content = ""
        previous_content = ""
    time.sleep(5)
    previous_file = r"C:\Users\kevin\Downloads\previous.txt"
    new_file = r"C:\Users\kevin\Downloads\[LINE]test line bot.txt"
    if os.path.exists(new_file):
        os.remove(new_file)
    subprocess.run([r"C:\Users\kevin\Downloads\save.exe"])
    with open(new_file, 'r', encoding='utf-8') as f:
        input_message.new_content = f.read().strip()
    with open(previous_file, 'w', encoding='utf-8') as f:
            f.write(input_message.new_content)  # 寫入內容 
    os.remove(new_file)
    while True:
        previous_file =r"C:\Users\kevin\Downloads\previous.txt"
        new_file = r"C:\Users\kevin\Downloads\[LINE]test line bot.txt"
        time.sleep(5)
        subprocess.run([r"C:\Users\kevin\Downloads\save.exe"])
        time.sleep(0.2)
        with open(previous_file, 'r', encoding='utf-8') as f:
            input_message.previous_content = f.read().strip()
        # 讀取 new
        with open(new_file, 'r', encoding='utf-8') as f:
            input_message.new_content = f.read().strip()
        # 比較內容
        if input_message.new_content != input_message.previous_content:
            extract_registration(input_message.new_content)
            time.sleep(0.2)
            if clipboard.new_output_message != clipboard.temp_output_message:    
                pyperclip.copy(clipboard.new_output_message)
                subprocess.run([r"C:\Users\kevin\Downloads\paste.exe"])
                clipboard.temp_output_message = clipboard.new_output_message
            else:
                print(f"{clipboard.new_output_message}及{clipboard.temp_output_message}")
            with open(previous_file, 'w', encoding='utf-8') as f:
                f.write(input_message.new_content)

        os.remove(new_file)
        time.sleep(5)

