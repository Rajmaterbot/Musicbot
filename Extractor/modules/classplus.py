import requests, os, sys, re
import json, asyncio
import subprocess
import datetime
from Extractor import app
from config import SUDO_USERS
from pyrogram import filters, idle
from subprocess import getstatusoutput




api = 'https://api.classplusapp.com/v2'

# ------------------------------------------------------------------------------------------------------------------------------- #

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


 # ------------------------------------------------------------------------------------------------------------------------------- #


def get_course_content(session, course_id, folder_id=0):
        fetched_contents = ""

        params = {
            'courseId': course_id,
            'folderId': folder_id,
        }

        res = session.get(f'{api}/course/content/get', params=params)

        if res.status_code == 200:
            res_json = res.json() 

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
                        "x-access-token": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpZCI6OTIzNDIwMDUsIm9yZ0lkIjo1NDI0MjEsInR5cGUiOjEsIm1vYmlsZSI6IjkxODI5ODczMDAzNiIsIm5hbWUiOiJTdWRoYW5zaHUgSmhhIiwiZW1haWwiOiJzdWRoYW5zaHVqaGExNTFAZ21haWwuY29tIiwiaXNJbnRlcm5hdGlvbmFsIjowLCJkZWZhdWx0TGFuZ3VhZ2UiOiJFTiIsImNvdW50cnlDb2RlIjoiSU4iLCJjb3VudHJ5SVNPIjoiOTEiLCJ0aW1lem9uZSI6IkdNVCs1OjMwIiwiaXNEaXkiOnRydWUsIm9yZ0NvZGUiOiJ1Y3Z2YW8iLCJpc0RpeVN1YmFkbWluIjowLCJmaW5nZXJwcmludElkIjoiOGE5NTlhMGQ1Y2UyNjBkNzJhMDVhMzcxYTBhYzk5YmUiLCJpYXQiOjE3MDc0OTc2OTAsImV4cCI6MTcwODEwMjQ5MH0.68JhYbWAjf1B0a6hD4OGSmVhhH2WF97DX8DMJAfo5CkIwIVWABMugHN0Mz43LUoY",
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
                    url = r.json()['url']

                    content = f'{name}:{url}\n'
                    fetched_contents += content

                else:
                    name = content.get('name', '')
                    url = content.get('url', '')
                    content = f'{name}:{url}\n'
                    fetched_contents += content

        return fetched_contents



# ------------------------------------------------------------------------------------------------------------------------------- #

async def classplus_txt(app, message):   

    headers = {
        'accept-encoding': 'gzip',
        'accept-language': 'EN',
        'api-version'    : '35',
        'app-version'    : '1.4.73.2',
        'build-number'   : '35',
        'connection'     : 'Keep-Alive',
            if res.status_code == 200:
                res = res.json()

                courses = res['data']['responseData']['coursesData']

                if courses:
                    text = ''

                    for cnt, course in enumerate(courses):
                        name = course['name']
                        text += f'{cnt + 1}. {name}\n'

                    reply = await message.chat.ask(
                        (
                            '**'
                            'Send index number of the course to download.\n\n'
                            f'{text}'
                            '**'
                        ),
                        reply_to_message_id = reply.id
                    )

                    if reply.text.isdigit() and len(reply.text) <= len(courses):

                        selected_course_index = int(reply.text.strip())

                        course = courses[selected_course_index - 1]

                        selected_course_id = course['id']
                        selected_course_name = course['name']

                        loader = await reply.reply(
                            (
                                '**'
                                'Extracting course...'
                                '**'
                            ),
                            quote=True
                        )

                        course_content = get_course_content(session, selected_course_id)

                        await loader.delete()

                        if course_content:

                            caption = (f"App Name : Classplus\nBatch Name : {selected_course_name}")

                            
                            text_file = "Classplus"
                            with open(f'{text_file}.txt', 'w') as f:
                                f.write(f"{course_content}")

                            await app.send_document(message.chat.id, document=f"{text_file}.txt", caption=caption)

                            html_file = f'{text_file}.html'
                            create_html_file(html_file, selected_course_name, course_content)

                            await app.send_document(message.chat.id, html_file, caption=caption)
                            os.remove(f'{text_file}.txt')
                            os.remove(html_file)
                            

                        else:
                            raise Exception('Did not found any content in course.')
                    raise Exception('Failed to validate course selection.')
                raise Exception('Did not found any course.')
            raise Exception('Failed to get courses.')
            

   
    except Exception as e:
        print(f"Error: {e}")
