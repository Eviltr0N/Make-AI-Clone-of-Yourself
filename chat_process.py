import re
import os
import shutil
import csv

chat_dir = "chats"

filler_words = ["ok", "hn", "Okay"]
class Wh_Chat_Processor:
    def __init__(self):
        pass
    def open_chat_file(self, dir,filename):
        self.sender_name = filename.replace("WhatsApp Chat with ", "").replace(".txt", "")
        with open(os.path.join(dir,filename)) as f:
            chat_text = f.read()
        return chat_text
    
    def msg_filter_basic(self, chat_text):
        filtered = []
        pt = r' - ([^:]+): (.*?)(?=\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s*(?:AM|PM|am|pm)? - |$)'
        msgs = re.findall(pt, chat_text, re.DOTALL)
        for msg in msgs:
            line = msg[1]
            wh_default_filter = "Tap to learn more." in line or "<Media omitted>" in line
            website_filter = "https://" in line or "http://" in line
            mail_filter = "@gmail.com" in line
            deleted_msg_filter = "This message was deleted" in line or "You deleted this message" in line or "<This message was edited>" in line or "(file attached)" in line

            if not (wh_default_filter or website_filter or mail_filter or deleted_msg_filter):
                    filtered.append(msg)
        return filtered

    def process_chat(self, chat_data):
        merged_lines = []
        current_sender = None
        current_message = {}
        for line in chat_data:
            if not line:
                continue
            parts = line
            if len(parts) == 2:
                sender, message = parts
                if current_sender is None:
                    current_sender = sender
                    current_message[current_sender] = [message.strip()]
                elif sender == current_sender:
                    current_message[current_sender].append(message.strip())
                else:
                    merged_lines.append(current_message)
                    current_sender = sender
                    current_message = {current_sender: [message.strip()]}
            else:
                if current_sender:
                    current_message[current_sender][-1] += " " + line.strip()
        if current_sender:
            merged_lines.append(current_message)
        keys = set() 
        for line in merged_lines:
            # print(line)
            for key in line.keys():
                if key != self.sender_name:
                    keys.add(key)
        self.my_name = list(keys)[0]
        print(list(keys))
        return merged_lines

    def advance_filter(self, merged_chat_data):
        filtered_data=[]
        sender = ""
        me = ""
        chk = 1
        CD = merged_chat_data
        for ind, x in enumerate(CD):
            if x.get(self.sender_name) != None :
                if len(x[self.sender_name]) == 1 and ( x[self.sender_name][0] in filler_words or len(x[self.sender_name][0]) ==1 ):
                    continue      
                if len(CD[ind][self.sender_name]) > 1:
                    for y in range(0,len(CD[ind][self.sender_name])):
                        if y+1 != len(CD[ind][self.sender_name]):
                            sender += CD[ind][self.sender_name][y] + "\n"
                        else:
                            sender += CD[ind][self.sender_name][y]
                else:
                    sender += CD[ind][self.sender_name][0]
            elif x.get(self.my_name) != None and len(sender) > 1:
                if len(CD[ind][self.my_name]) > 1:
                    for y in range(0,len(CD[ind][self.my_name])):
                        if y+1 != len(CD[ind][self.my_name]):
                            me += CD[ind][self.my_name][y] + "\n"
                        else:
                            me += CD[ind][self.my_name][y]
                else:
                    me += CD[ind][self.my_name][0]
            else:
                continue
            if chk ==1:
                chk+=1
            elif chk ==2:
                filtered_data.append([sender, me])
                sender = ""
                me=""
                chk=1
            else:
                pass
        return filtered_data

with open("all_chat_data.csv", "w") as f:
    f.write("Prompt,Response"+ "\n")

for file in os.listdir(os.path.join(chat_dir)):
    if file.endswith('.zip'):
        full_path = os.path.join(chat_dir, file)
        shutil.unpack_archive(full_path, chat_dir)

for file in os.listdir(os.path.join(chat_dir)):
    processor = Wh_Chat_Processor()
    if file.endswith('.txt'):
        print("Processing: ",file)
        chat_d = processor.open_chat_file(chat_dir,file)
        basic_f = processor.msg_filter_basic(chat_d)
        chat_ps = processor.process_chat(basic_f)
        filtered_data = processor.advance_filter(chat_ps)
        with open("all_chat_data.csv", "a") as f:
            csv_writer = csv.writer(f)
            for row in filtered_data:
                csv_writer.writerow(row)