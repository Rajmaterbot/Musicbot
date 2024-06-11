import requests
import json
import os

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
                    # Headers for video download
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


def classplus_txt(message):
    try:
        creds = input("SEND YOUR CREDENTIALS AS SHOWN BELOW\n\nORGANISATION CODE:\n\nPHONE NUMBER:\n\nOR SEND\nACCESS TOKEN:")

        session = requests.Session()

        if '\n' in creds:
            org_code, phone_no = [cred.strip() for cred in creds.split('\n')]

            if org_code.isalpha() and phone_no.isdigit() and len(phone_no) == 10:
                res = session.get(f'{api}/orgs/{org_code}')

                if res.status_code == 200:
                    res = res.json()

                    org_id = int(res['data']['orgId'])

                    data = {
                        'countryExt': '91',
                        'mobile'    : phone_no,
                        'orgCode'   : org_code,
                        'orgId'     : org_id,
                        'viaSms'    : 1,
                    }
        
                    res = session.post(f'{api}/otp/generate', data=json.dumps(data))

                    if res.status_code == 200:
                        res = res.json()

                        session_id = res['data']['sessionId']

                        otp = input("Send your otp: ")

                        if otp.isdigit():
                            data = {
                                "otp": otp,
                                "countryExt": "91",
                                "sessionId": session_id,
                                "orgId": org_id,
                                "fingerprintId": "",
                                "mobile": phone_no
                            }

                            res = session.post(f'{api}/users/verify', data=json.dumps(data))
                            res = res.json()
                            if res['status'] == 'success':
                                user_id = res['data']['user']['id']
                                token = res['data']['token']
                                session.headers['x-access-token'] = token
                            else:
                                raise Exception('Failed to verify OTP.')  
                        else:
                            raise Exception('Invalid OTP format.')
                    else:
                        raise Exception('Failed to generate OTP.')    
                else:
                    raise Exception('Failed to get organization Id.')
            else:
                raise Exception('Invalid credentials format.')

        else:
            token = creds.strip()
            session.headers['x-access-token'] = token

            res = session.get(f'{api}/users/details')

            if res.status_code == 200:
                res = res.json()

                user_id = res['data']['responseData']['user']['id']
            else:
                raise Exception('Failed to get user details.')

        params = {
            'userId': user_id,
            'tabCategoryId': 3
        }

        res = session.get(f'{api}/profiles/users/data', params=params)

        if res.status_code == 200:
            res = res.json()

            courses = res['data']['responseData']['coursesData']

            if courses:
                text = ''

                for cnt, course in enumerate(courses):
                    name = course['name']
                    text += f'{cnt + 1}. {name}\n'

                selected_course_index = int(input(f"Send index number of the course to download\n\n{text}: "))
                
                if 0 < selected_course_index <= len(courses):
                    course = courses[selected_course_index - 1]

                    selected_course_id = course['id']
                    selected_course_name = course['name']

                    course_content = get_course_content(session, selected_course_id)

                    if course_content:
                        caption = (f"App Name : Classplus\nBatch Name : {selected_course_name}")

                        text_file = "Classplus"
                        with open(f'{text_file}.txt', 'w') as f:
                            f.write(f"{course_content}")

                        print(f"Course content saved to {text_file}.txt")

                        html_file = f'{text_file}.html'
                        create_html_file(html_file, selected_course_name, course_content)

                        print(f"HTML file created: {html_file}")

                        os.remove(f'{text_file}.txt')
                        os.remove(html_file)
                    else:
                        raise Exception('Did not found any content in course.')
                else:
                    raise Exception('Invalid course index.')
            else:
                raise Exception('Did not found any course.')
        else:
            raise Exception('Failed to get courses.')

    except Exception as e:
        print(f"Error: {e}")

classplus_txt()

