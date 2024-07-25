from WPP_Whatsapp import Create
from langchain_core.messages import HumanMessage, AIMessage
import logging
import csv
from chat import LLM

#========LLM(Model_name, temperature, top_k, max_tokens)

my_llm = LLM("my_model", 0.3, 50, 128)

# logger = logging.getLogger(name="WPP_Whatsapp")
# logger.setLevel(logging.DEBUG)


your_session_name = "test"
creator = Create(session=your_session_name)


client = creator.start()


if creator.state != 'CONNECTED':
    raise Exception(creator.state)


def save_chat(ph_number, msg):
    with open(f'{ph_number}.csv', "a") as f:
        csv_writer = csv.DictWriter(f, fieldnames=["USER", "AI"])
        csv_writer.writerow(msg)

def new_message(message):
    global client, gender

    if message and not message.get("isGroupMsg"):
        chat_id = message.get("from")
        message_id = message.get("id")
        if chat_id==f'{ph_number}@c.us':
            print("Sender: ", message.get("body"))
            client.sendSeen(chat_id)
            res = my_llm.chat(message.get("body"))
            print("AI: ", res)
            client.startTyping(chat_id)
            res_list = res.split("\n ")
            client.reply(chat_id, res_list[0], message_id)
            client.stopTyping(chat_id)
            for msg in range(1, len(res_list)):
                client.startTyping(chat_id)
                client.sendText(chat_id, res_list[msg])
            client.stopTyping(chat_id)
            save_chat(ph_number, {"USER": message.get("body"), "AI": res})

creator.client.ThreadsafeBrowser.page_evaluate_sync("""
 // Resolvenndo bug 'TypeError: i.Wid.isStatusV3 is not a function'
    if(!WPP.whatsapp.Wid.isStatusV3) {
      WPP.whatsapp.Wid.isStatusV3 = () => false
    }
""")



ph_number = input("Enter Ph. No. with Countary code: ")
while len(ph_number) < 12:
    ph_number = input("WITH Countary Code: ")



creator.client.onMessage(new_message)
creator.loop.run_forever()