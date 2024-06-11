import json
import os
import requests
import threading
import asyncio
import logging
import cloudscraper
from pyrogram import Client, filters
from pyrogram.types import Message
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

# Config module and Extractor app setup
import config
from Extractor import app

logging.basicConfig(level=logging.INFO)

# Decryption function
def decrypt_data(encoded_data):
    key = "638udh3829162018".encode("utf8")
    iv = "fedcba9876543210".encode("utf8")
    decoded_data = b64decode(encoded_data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
    return decrypted_data.decode('utf-8')

# Function to fetch all topics from a course
def fetch_topics(api, course_id, subject_id, headers):
    response = requests.get(
        f"https://{api}/get/alltopicfrmlivecourseclass",
        params={"courseid": course_id, "subjectid": subject_id},
        headers=headers
    )
    return response.json().get('data', [])

# Function to fetch video links by topic
def fetch_video_links(api, course_id, subject_id, topic_id, headers):
    response = requests.get(
        f"https://{api}/get/livecourseclassbycoursesubtopconceptapiv3",
        params={
            "topicid": topic_id,
            "start": -1,
            "courseid": course_id,
            "subjectid": subject_id
        },
        headers=headers
    )
    return response.json().get('data', [])

# Process each topic's materials
def process_material(data):
    material_type = data.get('material_type')
    title = data.get("Title")
    result = []

    if material_type == 'VIDEO':
        result.extend(process_video(data, title))
    elif material_type == 'PDF':
        result.append(process_pdf(data, title))
    return result

# Process video material
def process_video(data, title):
    result = []
    if data.get('pdf_link'):
        pdf_link = data.get('pdf_link').split(':')
        if len(pdf_link) == 2:
            encoded_part = pdf_link[0]
            decrypted_link = decrypt_data(encoded_part)
            result.append(f"{title} : {decrypted_link}")

    if data.get('ytFlag') == 0 and data.get('ytFlagWeb') == 0:
        download_links = data.get('download_links', [])
        dlink = next((link['path'] for link in download_links if link.get('quality') == "720p"), None)
        if dlink:
            encoded_part = dlink.split(':')[0]
            decrypted_link = decrypt_data(encoded_part)
            result.append(f"{title} : {decrypted_link}")

    elif data.get('ytFlag') == 1:
        dlink = data.get('file_link')
        if dlink:
            encoded_part = dlink.split(':')[0]
            decrypted_link = decrypt_data(encoded_part)
            video_id = decrypted_link.split('/')[-1] if data.get('ytFlagWeb') == 0 else decrypted_link
            result.append(f"{title} : https://youtu.be/{video_id}")
    return result

# Process PDF material
def process_pdf(data, title):
    pdf_link = data.get("pdf_link", "").split(':')
    if len(pdf_link) == 2:
        encoded_part = pdf_link[0]
        decrypted_link = decrypt_data(encoded_part)
        return f"{title} : {decrypted_link}"
    return f"{title} : Missing PDF link"

# Download materials from a specific course
async def download_course_materials(app, message, headers, api, course_id, subject_ids, batch_name, app_name):
    vt = ""
    for subject_id in subject_ids.split('&'):
        if not subject_id:
            continue
        topics = fetch_topics(api, course_id, subject_id, headers)
        for topic in topics:
            topic_id = topic.get("topicid")
            if not topic_id:
                continue
            materials = fetch_video_links(api, course_id, subject_id, topic_id, headers)
            for material in materials:
                vt += "\n".join(process_material(material)) + "\n"

    file_name = f"{batch_name}.txt"
    with open(file_name, 'w') as f:
        f.write(vt)

    await app.send_document(
        message.chat.id, document=file_name, 
        caption=f"**App Name :- {app_name}\nBatch Name :-** `{batch_name}`"
    )
    os.remove(file_name)
    await message.reply_text("Done")

# Login and fetch courses
async def login_and_fetch_courses(api, credentials):
    raw_url = f"https://{api}/post/userLogin"
    hdr = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1"
    }
    scraper = cloudscraper.create_scraper()
    res = scraper.post(raw_url, data=credentials, headers=hdr).content
    output = json.loads(res)
    return output

# Fetch subjects of a specific course
def fetch_subjects(api, course_id, headers):
    response = requests.get(
        f"https://{api}/get/allsubjectfrmlivecourseclass",
        params={"courseid": course_id},
        headers=headers
    )
    return response.json().get('data', [])

# Main function to handle the command
@app.on_message(filters.command("download_course"))
async def handle_download_course(app, message):
    input1 = await app.ask(
        message.chat.id, 
        text="Send **ID & Password** in this manner, otherwise, the bot will not respond.\n\nSend like this: **ID*Password**"
    )
    raw_text = input1.text
    email, password = raw_text.split("*")
    credentials = {"email": email, "password": password}
    await input1.delete(True)

    try:
        output = await login_and_fetch_courses(config.API_URL, credentials)
        userid = output["data"]["userid"]
        token = output["data"]["token"]
        headers = {
            "Host": config.API_URL,
            "Client-Service": "Appx",
            "Auth-Key": "appxapi",
            "User-Id": userid,
            "Authorization": token
        }
        await message.reply_text("**Login Successful**")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        await message.reply_text("Login failed. Please check your credentials and try again.")
        return

    res1 = requests.get(f"https://{config.API_URL}/get/mycourseweb?userid={userid}", headers=headers)
    b_data = res1.json().get('data', [])
    course_info = "\n".join([f"**`{data['id']}` - `{data['course_name']}`**" for data in b_data])
    await message.reply_text(f"**YOU HAVE THESE BATCHES:**\n\nBATCH-ID - BATCH NAME - INSTRUCTOR\n\n{course_info}")

    input2 = await app.ask(message.chat.id, text="**Now send the Batch ID to Download**")
    raw_text2 = input2.text

    batch_name = next((data['course_name'] for data in b_data if data['id'] == raw_text2), "Unknown Batch")
    subjID_data = fetch_subjects(config.API_URL, raw_text2, headers)
    subjIDs = "&".join(str(sub["subjectid"]) for sub in subjID_data)

    prog = await message.reply_text("**Extracting Videos Links Please Wait 📥 **")
    thread = threading.Thread(target=lambda: asyncio.run(
        download_course_materials(app, message, headers, config.API_URL, raw_text2, subjIDs, batch_name, "App Name")
    ))
    thread.start()
