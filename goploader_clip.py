#!/usr/bin/python3
import subprocess
import datetime
import requests
import validators


def run(bashCommand, stdin=None):

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if stdin is not None:
        process.stdin.write(stdin.encode('utf-8'))
    output, error = process.communicate()
    return output, error


def sendFile(file, name):
    s = requests.Session()
    s.headers = {'User-Agent': 'curl/angel'}
    try:
        result = s.post('http://172.16.0.3:8096/', files=dict(file=file, name=name))
    except:
        print('Server Error!')
        return None
    if result.status_code != 201:
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
                text = '<!DOCTYPE html><meta http-equiv="refresh" content="0;url=' + text + '" />'
            sendFile(text.encode('utf-8'), name)


if __name__ == '__main__':
    main()
