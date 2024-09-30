from pyrogram import Client
from pyrogram.errors import FloodWait
from dotenv import load_dotenv
import os
import json

load_dotenv("requiredParameters.env")
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
#api_id = "26104699"
#api_hash = "f8c6d5b3db9ac050363b1446aa9b2ca7"
parent_download_folder = "downloaded_breach_data"
downloaded_filename = "GODELESS CLOUD.txt"

app = Client("my_account",api_id,api_hash)
scraped_chats = json.loads(os.getenv("TELEGRAM_CHATS"))
#scraped_chats =  {"GODELESS CLOUD" : -1001555839565}
def telegramScraper(scraped_chats):
    """ function that downloads breach data files from telegram channels   
        input : - scraped_chats : dictionnary of telegram chats (keys) and telegram chat ids (values)
        output : downloads breach data in "downloadfolder/chatname"
    """
    with app:
        for chat_name in scraped_chats.keys():
            i = 0
            download_folder = f"{parent_download_folder}/{chat_name}"
            for message in app.get_chat_history(scraped_chats[chat_name]):
                if message.document:
                    file_name = message.document.file_name
                    if file_name.endswith("txt"):
                        outputfile = f"{i}.txt"
                        download_successful = False
                        while not download_successful:
                            try:
                                print("Downloading breach file", i)
                                file_path =  app.download_media(message.document.file_id, file_name=os.path.join(download_folder, outputfile))
                                download_successful = True
                            except FloodWait as e:
                                print("Server Flood, need to wait : ", end="")
                                wait_time = e.value
                                print(e.value, end="")
                                time.sleep(wait_time)
                                #except Exception as e:
                                #    print(e)
                                #    wait_time = e.value
                                #    print("Server Flood, need to wait", wait_time)
                            #    time.sleep(wait_time)
                        i += 1

if __name__ == "__main__":
     app.run(telegramScraper(scraped_chats))
