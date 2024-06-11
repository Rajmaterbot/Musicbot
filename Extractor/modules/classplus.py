import requests
import os
import json
from pyrogram import filters, idle

api = 'https://api.classplusapp.com/v2'

def create_html_file(file_name, batch_name, contents):
    tbody = ''
    parts = contents.split('\n')
    for part in parts:
        split_part = [item.strip() for item in part.split(':', 1)]

        text = split_part[0] if split_part[0] else 'Untitled'
        url = split_part[1].strip() if len(split_part) > 1 and split_part[1].strip() else 'No URL'

        tbody += f'<tr><td>{text}</td><td><a href="{url}" target="_blank">{url}</a></td></tr>'

    with open('Extractor/core/template.html', 'r') as fp:
        file_content = fp.read()
    title = batch_name.strip()
    with open(file_name, 'w') as fp:
        fp.write(file_content.replace('{{tbody_content}}', tbody).replace('{{batch_name}}', title))

def get_course_content(session, course_id, folder_id=0):
    fetched_contents = ""

    params = {
        'courseId': course_id,
        'folderId': folder_id,
    }

    res = session.get(f'{api}/course/content/get', params=params)

    if res.status_code == 200:
        try:
            res_json = res.json()
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {res.text}")
            return ""

        contents = res_json.get('data', {}).get('courseContent', [])

        for content in contents:
            if content['contentType'] == 1:
                resources = content.get('resources', {})

                if resources.get('videos') or resources.get('files'):
                    sub_contents = get_course_content(session, course_id, content['id'])
                    fetched_contents += sub_contents

            elif content['contentType'] == 2:
                name = content.get('name', '')
                id = content.get('contentHashId', '')

                headers = {
                    "Host": "api.classplusapp.com",
                    "x-access-token": "YOUR_ACCESS_TOKEN_HERE",
                    "User-Agent": "Mobile-Android",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en",
                    "Origin": "https://web.classplusapp.com",
                    "Referer": "https://web.classplusapp.com/",
                    "Region": "IN",
                    "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": "\"Windows\"",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                }

                params = {
                    'contentId': id
                }

                r = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                try:
                    url = r.json()['url']
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON response for video URL: {r.text}")
                    url = "No URL"

                content = f'{name}:{url}\n'
                fetched_contents += content

            else:
                name = content.get('name', '')
                url = content.get('url', '')
                content = f'{name}:{url}\n'
                fetched_contents += content

    return fetched_contents

async def classplus_txt(app, message):

    headers = {
        'accept-encoding': 'gzip',
        'accept-language': 'EN',
        'api-version': '35',
        'app-version': '1.4.73.2',
        'build-number': '35',
        'connection': 'Keep-Alive',
        'content-type': 'application/json',
        'device-details': 'Xiaomi_Redmi 7_SDK-32',
        'device-id': 'c28d3cb16bbdac01',
        'host': 'api.classplusapp.com',
        'region': 'IN',
        'user-agent': 'Mobile-Android',
        'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c'
    }

    headers2 = {
        "Api-Version": "43",
        "Content-Type": "application/json;charset=UTF-8",
        "Device-Id": "1706954623055",
        "Origin": "https://web.classplusapp.com",
        "Referer": "https://web.classplusapp.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }

    try:
        input = await app.ask(message.chat.id, text="SEND YOUR CREDENTIALS AS SHOWN BELOW\n\nORGANISATION CODE:\n\nPHONE NUMBER:\n\nOR SEND\nACCESS TOKEN:")

        creds = input.text
        session = requests.Session()
        session.headers.update(headers2)

        logged_in = False

        if '\n' in creds:
            org_code, phone_no = [cred.strip() for cred in creds.split('\n')]

            if org_code.isalpha() and phone_no.isdigit() and len(phone_no) == 10:
                res = session.get(f'{api}/orgs/{org_code}')

                if res.status_code == 200:
                    try:
                        res = res.json()
                    except json.JSONDecodeError:
                        await message.reply_text(f"Failed to decode JSON response: {res.text}")
                        return

                    org_id = int(res['data']['orgId'])

                    data = {
                        'countryExt': '91',
                        'mobile': phone_no,
                        'orgCode': org_code,
                        'orgId': org_id,
                        'viaSms': 1,
                    }

                    res = session.post(f'{api}/otp/generate', data=json.dumps(data))

                    if res.status_code == 200:
                        try:
                            res = res.json()
                        except json.JSONDecodeError:
                            await message.reply_text(f"Failed to decode JSON response: {res.text}")
                            return

                        session_id = res['data']['sessionId']

                        user_otp = await app.ask(message.chat.id, text="Send your OTP")

                        if user_otp.text.isdigit():
                            otp = user_otp.text.strip()

                            data = {
                                "otp": otp,
                                "countryExt": "91",
                                "sessionId": session_id,
                                "orgId": org_id,
                                "fingerprintId": "",
                                "mobile": phone_no
                            }

                            res = session.post(f'{api}/users/verify', data=json.dumps(data))
                            try:
                                res = res.json()
                            except json.JSONDecodeError:
                                await message.reply_text(f"Failed to decode JSON response: {res.text}")
                                return

                            if res['status'] == 'success':
                                await app.send_message(message.chat.id, res)
                                user_id = res['data']['user']['id']
                                token = res['data']['token']
                                session.headers['x-access-token'] = token

                                await message.reply_text(f"Your access token for future uses -\n\n{token}")

                                logged_in = True

                            else:
                                await message.reply_text(f'Failed to verify OTP: {res}')
                        else:
                            await message.reply_text('Invalid OTP format.')
                    else:
                        await message.reply_text(f'Failed to generate OTP: {res.text}')
                else:
                    await message.reply_text(f'Failed to get organization ID: {res.text}')
            else:
                await message.reply_text('Invalid credentials format.')

        else:
            token = creds.strip()
            session.headers['x-access-token'] = token

            res = session.get(f'{api}/users/details')

            if res.status_code == 200:
                try:
                    res = res.json()
                except json.JSONDecodeError:
                    await message.reply_text(f"Failed to decode JSON response: {res.text}")
                    return

                user_id = res['data']['responseData']['user']['id']
                logged_in = True

            else:
                await message.reply_text(f'Failed to get user details: {res.text}')

        if logged_in:
            params = {
                'userId': user_id,
                'tabCategoryId': 3
            }

            res = session.get(f'{api}/profiles/users/data', params=params)

            if res.status_code == 200:
                try:
                    res = res.json()
                except json.JSONDecodeError:
                    await message.reply_text(f"Failed to decode JSON response: {res.text}")
                    return

                courses = res['data']['responseData']['coursesData']

                if courses:
                    text = ''

                    for cnt, course in enumerate(courses):
                        name = course['name']
                        text += f'{cnt + 1}. {name}\n'

                    num = await app.ask(message.chat.id, text=f"send index number of the course to download\n\n{text}")

                    if num.text.isdigit() and 1 <= int(num.text.strip()) <= len(courses):

                        selected_course_index = int(num.text.strip())

                        course = courses[selected_course_index - 1]

                        selected_course_id = course['id']
                        selected_course_name = course['name']

                        msg = await message.reply_text("Now extracting your course")

                        course_content = get_course_content(session, selected_course_id)
                        await msg.delete()

                        if course_content:

                            caption = (f"App Name : Classplus\nBatch Name : {selected_course_name}")

                            text_file = f"{selected_course_name}.txt"
                            with open(text_file, 'w') as f:
                                f.write(f"{course_content}")

                            await app.send_document(message.chat.id, document=text_file, caption=caption)

                            html_file = f'{selected_course_name}.html'
                            create_html_file(html_file, selected_course_name, course_content)

                            await app.send_document(message.chat.id, html_file, caption=caption)
                            os.remove(text_file)
                            os.remove(html_file)

                        else:
                            await message.reply_text('No content found in the course.')
                    else:
                        await message.reply_text('Invalid input. Please send a valid course index number.')
                else:
                    await message.reply_text('No courses found for this user.')
            else:
                await message.reply_text(f'Failed to get user profile data: {res.text}')

    except Exception as e:
        await message.reply_text(f'An error occurred: {str(e)}')

# Assuming this function is registered in your bot with Pyrogram
# app.add_handler(filters.command("classplus_txt"), classplus_txt)
