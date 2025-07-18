

import time
import subprocess
import re
import sys
import chardet
import os
import pyperclip
import io
from datetime import datetime

def extract_registration(text):
    output_message = ""

    # 定義包含「場館資訊」和「時段及成員資訊」的完整區塊
    full_section_pattern = r'❣️.*?❣️.*?.(?=❣️.*?❣️.*?.|\Z)'
    sections = re.findall(full_section_pattern, text, re.DOTALL)
    if sections:
        # 取出最後一個完整區塊
        last_section = sections[-1]
        info_section = re.search(r'❣️.*?❣️.*?\n——————————————', last_section, re.DOTALL)
        output_message += info_section.group() + "\n"

        session_pattern = r'([A-Za-z])\.?時段\s?\(?(\d{2}:\d{2})\~?\-?(\d{2}:\d{2})\)?(.*?)(?=[A-Za-z]\.?時段\s?|\Z)'
        sessions = re.findall(session_pattern, last_section, re.DOTALL)

        if sessions:
            sessions_str = re.findall(r'[A-Za-z]\.?時段\s?\(?\d{2}:\d{2}\~?\-?\d{2}:\d{2}\)?.*?(?=[A-Za-z]\.?時段\s?|\Z)', last_section, re.DOTALL)
            for session, session_str in zip(sessions, sessions_str):
                session_info = re.search(r'[A-Za-z]\.?時段.*?(?=\n1\.)', session_str, re.DOTALL)
                time_slot = session[0]  # 時段標記    
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                total_minutes = current_hour * 60 + current_minute
                start_time = session[1]
                session_start_time = re.match(r'(\d{2}):(\d{2})', start_time)
                session_start_time = int(session_start_time.group(1)) * 60 + int(session_start_time.group(2))
                #if total_minutes > 1140:
                #    input_message.show_all_session = "True"
                #else:
                #    input_message.show_all_session = "False"
                if total_minutes > session_start_time and input_message.show_all_session == "False":
                   continue
                output_message += session_info.group() + "\n"

                end_time = session[2] 
                members = session[3].strip().splitlines()

                member_list = []
                for member in members:
                    member = member.strip()
                    match = re.match(r'^(候補)?(\d{1,2})\.(.*?)(?=\s\d{1,2}|\Z)', member)
                    if match:
                        if not match.group(1) == "候補":
                            max_index = int(match.group(2))
                        name = match.group(3).strip()
                        if name != "":
                            member_list.append(name)

                client_register_message_pattern = r'(\d{1,2}):(\d{2})\s(.*?)\s([A-Za-z])([+\-加減])(\d{1,2})\s?(.*?)?'
                client_register_messages = re.findall(client_register_message_pattern, last_section, flags=re.DOTALL)

                if client_register_messages:
                    for client_register_message in client_register_messages:
                        if client_register_message[6]:
                            client_register_name = client_register_message[6]
                        else:
                            client_register_name = client_register_message[2]
                        client_register_session = client_register_message[3].upper()
                        client_register_in_out = client_register_message[4]
                        client_register_in_out_times = int(client_register_message[5])
                        if client_register_session == time_slot:
                            if client_register_in_out == "+":
                                for _ in range(client_register_in_out_times):
                                    member_list.append(client_register_name)
                            elif client_register_in_out == "-":
                                for _ in range(client_register_in_out_times):
                                    if client_register_name in member_list:
                                        member_list.remove(client_register_name)

                index = 0
                last_printed_name = ""
                print_times = 1
                for index, name in enumerate(member_list, start=1):
                    if index > max_index:
                        index_display = f"候補{index - max_index}"
                    else:
                        index_display = f"{index}"
                    if name == last_printed_name:
                        print_times += 1
                        output_message += f"{index_display}.{name} {print_times}\n"
                    else:
                        output_message += f"{index_display}.{name}\n"
                        last_printed_name = name
                        print_times = 1

                if isinstance(index, int):
                    while index < 2:
                        index += 1
                        output_message += f"{index}.\n"
                    if index < max_index - 2:
                        output_message += f"{index + 1}.\n…\n{max_index}.\n"
                    elif index == max_index - 2:
                        output_message += f"{index + 1}.\n{max_index}.\n"
                    elif index == max_index - 1:
                        output_message += f"{max_index}.\n"
                output_message += "——————————————\n"
        else:
            output_message += "未找到成員資訊中的時段和成員名單\n"
    else:
        output_message += "未找到包含場館資訊和時段及成員資訊的完整區塊\n"
    return output_message


    
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
        last_record_time = ""
        show_all_session = "False"
    time.sleep(5)
    previous_file = r"previous.txt"
    new_file = r"1.txt"
    if os.path.exists(new_file):
        os.remove(new_file)
    subprocess.run([r"save.exe"])
    with open(new_file, 'r', encoding='utf-8') as f:
        input_message.new_content = f.read().strip()
    with open(previous_file, 'w', encoding='utf-8') as f:
            f.write(input_message.new_content)  # 寫入內容 

    while True:
        previous_file =r"previous.txt"
        new_file = r"1.txt"
        subprocess.run([r"save.exe"])
        if not os.path.exists(new_file):
            continue
        time.sleep(10)
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
#                print(f"{clipboard.new_output_message}and{clipboard.temp_output_message}")
                subprocess.run([r"paste.exe"])
                clipboard.temp_output_message = clipboard.new_output_message
            else:
                print(f"{clipboard.new_output_message}及{clipboard.temp_output_message}")
            with open(previous_file, 'w', encoding='utf-8') as f:
                f.write(input_message.new_content)

#        os.remove(new_file)
        time.sleep(5)


