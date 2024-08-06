#! /usr/bin/env python3

'''
Simple Jekyll site manage script.
'''
import os
import sys
import time
import datetime
import signal
import argparse
import subprocess
from subprocess import Popen
import http.server
import socketserver

# Settings
HOSTNAME = 'ioover.net'
PATH = '/var/www/ioover.net/'
TIME_ZONE = '+0900'
DEPLOY_CMD = "rsync -rav --no-perms --delete ./_site/ rsync://10.110.1.1/blog"

# Formatting
POST_TEMPLATE = \
'''---
layout: post
title: {title}
date: {date:%Y-%m-%d %H:%M:%S} {timezone}
category:
summary:
typora-root-url: ../
typora-copy-images-to: ../media
---

'''


def run(command):
    print('+ ' + command)
    os.system(command)

def open_editor(filepath):
    ''' Open file with system default editor. '''
    # Refer to:
    # https://stackoverflow.com/a/435669
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        # pylint: disable=E1101
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))


def create_post(title: str):
    now = datetime.datetime.now()
    source = POST_TEMPLATE.format(title=title, date=now, timezone=TIME_ZONE)
    filename = '{:%Y-%m-%d-}{}.md'.format(now, title.replace(' ', '-').lower())
    path = os.path.join('posts', filename)
    if not os.path.exists(path):
        with open(path, mode='w', encoding='utf-8') as new:
            new.write(source)
    else:
        print('The file already exists.')
    open_editor(path)


def build():
    run('bundle exec jekyll build')

def serve():
    run('bundle exec jekyll serve')

def deploy():
    build()
    run("chmod 644 _posts/* media/*")
    run(DEPLOY_CMD)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('build', help='Build site from source.')
    subparsers.add_parser('deploy', help='Build and deploy site to server.')
    subparsers.add_parser('serve', help='Run development server.')
    post_parser = subparsers.add_parser('post', help='Create new post, then open.', aliases=['new', 'add'])
    post_parser.add_argument('title')

    args = parser.parse_args()
    if args.command == 'post':
        create_post(args.title)
    elif args.command == 'build':
        build()
    elif args.command == 'serve':
        serve()
    elif args.command == 'deploy':
        deploy()


if __name__ == '__main__':
    main()
