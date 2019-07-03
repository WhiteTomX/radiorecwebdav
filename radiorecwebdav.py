#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

"""
radiorec.py Recording and uploading internet radio streams
Copyright (C) 2013  Martin Brodbeck <martin@brodbeck-online.de>
Edited By WhiteTom

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import configparser
import datetime
import os
import stat
import sys
import threading
import urllib.request
import webdav3.client as wc
import tempfile
import time


def check_duration(value):
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Duration must be a positive integer.')

    if value < 1:
        raise argparse.ArgumentTypeError(
            'Duration must be a positive integer.')
    else:
        return value


def read_settings(args):
    config = configparser.ConfigParser()
    if args.settings:
        config.read_file(open(args.settings))
        return dict(config.items())
    paths = []
    if sys.platform.startswith('linux'):
        paths.append(os.getenv('HOME') + os.sep + '.config' + os.sep + 'radiorec')
    elif sys.platform == 'win32':
        paths.append(os.getenv('LOCALAPPDATA') + os.sep + 'radiorec')
    elif sys.platform == 'darwin':
        paths.append(os.getenv('HOME') + os.sep + 'Library' + os.sep + 'Application Support' + os.sep + 'radiorec')
    paths.append(os.path.dirname(os.path.abspath(__file__)))
    paths.append(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'settings' )

    success = False
    for path in paths:
        try:
            config.read_file(open(path + os.sep + 'settings.ini'))
            success = True
            break
        except FileNotFoundError:
            pass

    if success == True:
        return dict(config.items())
    else:
        raise FileNotFoundError


def get_remote_path(content_type, remote_dir, args):
    cur_dt_string = datetime.datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
    filename = remote_dir + os.sep + cur_dt_string + "_" + args.station
    if args.name:
        filename += '_' + args.name
    if(content_type == 'audio/mpeg'):
        filename += '.mp3'
    elif(content_type == 'application/ogg' or content_type == 'audio/ogg'):
        filename += '.ogg'
    elif(content_type == 'audio/x-mpegurl'):
        print('Sorry, M3U playlists are currently not supported')
        sys.exit()
    else:
        print('Unknown content type "' + content_type + '". Assuming mp3.')
        filename += '.mp3'
    return filename


def record(args):
    settings = read_settings(args)
    streamurl = ''
    global verboseprint
    verboseprint = print if args.verbose else lambda *a, **k: None

    try:
        streamurl = settings['STATIONS'][args.station]
    except KeyError:
        print('Unkown station name: ' + args.station)
        sys.exit()
    if streamurl.endswith('.m3u'):
        verboseprint('Seems to be an M3U playlist. Trying to parse...')
        with urllib.request.urlopen(streamurl) as remotefile:
            for line in remotefile:
                if not line.decode('utf-8').startswith('#') and len(line) > 1:
                    tmpstr = line.decode('utf-8')
                    break
        streamurl = tmpstr
    verboseprint('stream url: ' + streamurl)

    options = {
        'webdav_hostname': settings['WEBDAV']['url'],
        'webdav_login':    settings['WEBDAV']['user'],
        'webdav_password': settings['WEBDAV']['password']
    }
    webdav = wc.Client(options)
    webdav.free()

    conn = urllib.request.urlopen(streamurl)
    remote_path = get_remote_path(conn.getheader('Content-Type'), settings['WEBDAV']['remote_dir'], args)
    with tempfile.NamedTemporaryFile() as target:
        verboseprint('tempfile: ' + target.name)
        verboseprint('Recording ' + args.station + '...')
        timeout = args.duration * 60
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            target.write(conn.read(1024))
        verboseprint('uploading file to ' + remote_path)
        webdav.upload(remote_path, target.name)



def list(args):
    settings = read_settings(args)
    for key in sorted(settings['STATIONS']):
        print(key)


def main():
    parser = argparse.ArgumentParser(description='This program records internet radio streams and uploads them to webdav')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_record = subparsers.add_parser('record', help='Record a station')
    parser_record.add_argument('station', type=str,
                               help='Name of the radio station '
                               '(see `radiorec.py list`)')
    parser_record.add_argument('duration', type=check_duration,
                               help='Recording time in minutes')
    parser_record.add_argument('name', nargs='?', type=str,
                               help='A name for the recording')
    parser_record.add_argument(
        '-v', '--verbose', action='store_true', help="Verbose output")
    parser_record.add_argument(
        '-s', '--settings', nargs='?', type=str,
        help="specify alternative path to the settings file")
    parser_record.set_defaults(func=record)
    parser_list = subparsers.add_parser('list', help='List all known stations')
    parser_list.set_defaults(func=list)
    parser_list.add_argument(
        '-s', '--settings', nargs='?', type=str,
        help="specify alternative path to the settings file")

    if not len(sys.argv) > 1:
        print('Error: No argument specified.\n')
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
