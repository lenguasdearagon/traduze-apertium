import requests
from django.conf import settings
import time

def translate_string(text, source_language, target_language, engine, content_type="txt"):
    payload = {
        "text": text,
        "source_language": source_language,
        "target_language": target_language,
        "engine": engine,
        "content_type": content_type
    }
    r = requests.post(f"{settings.API_URL}/translate_string", data=payload)
    print(r.text)
    if r.status_code == 200:
        result = r.json()
        return result
    return None

def translate_file_api(filepath, source_language, target_language, engine, content_type):
    payload = {
        "source_language": source_language,
        "target_language": target_language,
        "engine": engine,
        "content_type": content_type
    }
    files = {
        "file": open(filepath, "rb")
    }
    r = requests.post(f"{settings.API_URL}/translate_file", data=payload, files=files)
    print(r.text)
    if r.status_code == 200:
        return r.json()["task_id"]
    return None

def fetch_file_api(task_id):
    payload = {
        "task_id": task_id
    }
    r = requests.post(f"{settings.API_URL}/fetch_file", data=payload)
    print(r.text)
    if r.status_code == 200:
        return r.json()["finished"], r.json()
    return True, None

def translate_file(filepath, source_language, target_language, engine, content_type):
    task_id = translate_file_api(filepath, source_language, target_language, engine, content_type)
    if task_id:
        print(f"File successfully posted to server for translation. Task: {task_id}")
        while True:
            finished, response = fetch_file_api(task_id)
            if finished:
                return response
            time.sleep(0.5)
    else:
        print("There was an error posting file to server for translation")
        return None
