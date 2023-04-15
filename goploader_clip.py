#!/usr/bin/python3
import datetime
import dotenv
import os
import requests
import subprocess
import validators

basic_auth = True
dotenv.load_dotenv()

def run(bashCommand, stdin=None):

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if stdin is not None:
        process.stdin.write(stdin.encode('utf-8'))
    output, error = process.communicate()
    return output, error


def sendFile(file, name):
    s = requests.Session()
    s.headers = {'User-Agent': 'curl/angel'}
    if basic_auth:
        USER = os.getenv('GOP_USER')
        PASSWORD = os.getenv('GOP_PASSWORD')
        s.auth = (USER, PASSWORD)
    try:
        result = s.post('https://paste.jouellet.net/add', files=dict(file=file, name=name))
    except:
        print('Server Error!', '-1')
        return None
    if result.status_code != 201:
        print('Server Error!', result.status_code)
        return None
    if result.text is not None:
        run('xclip -selection clipboard -t text/plain -i', stdin=result.text.strip())
        print('URL Copied to clipboard')
        print(result.text)
    return result.text


def main():
    xclip_target_output = run('xclip -selection clipboard -t TARGETS -o')
    if xclip_target_output[1] != b'':
        print("Clipboard Empty!")
    targets = xclip_target_output[0].decode('utf-8')
    if 'image/png' in targets:
        print('image')
        image = run('xclip -selection clipboard -t image/png -o')[0]
        sendFile(image, 'Image_' + str(datetime.datetime.now()) + '.png')
        return
    if 'text/plain' in targets:
        text = run('xclip -selection clipboard -t text/plain -o')[0].decode('utf-8')
        if text.startswith('file://'):
            print('file')
            if len(text.split('file:')) != 2:
                print('Cannot upload multiple files, try zipping first')
                return
            try:
                file = open(text.replace('file://', ''), 'br').read()
            except IsADirectoryError:
                print('Cannot upload a directory, try zipping it first.')
                return
            sendFile(file, text.split('/')[-1])
        else:
            print('text')
            name = 'text_' + str(datetime.datetime.now()) + '.txt'
            if validators.url(text) is True:
                if 'paste.jouellet.net' in text:
                    print('Link already in clipboard')
                    return
                if '172.16.0.3:2342/api/v1/t' in text or 'photos.jouellet.net/api/v1/t' in text:
                    parts = text.split('/')
                    url = '/'.join(parts[:8]) + '/fit_7680'
                    file = requests.get(url)
                    sendFile(file.content, 'image.jpeg')
                    return

                text = '<!DOCTYPE html><meta http-equiv="refresh" content="0;url=' + text + '" />'
            sendFile(text.encode('utf-8'), name)


if __name__ == '__main__':
    main()
