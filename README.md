# Requirements
* Python 3.x with argparse (which is already included in Python >= 3.2)
* webdavclient3

# Installation
1. Copy the Script wherever you want
2. Copy the config file settings.ini into your local settings directory, depending on which platform you are using this program, e.g.:
  * Linux: $HOME/.config/radiorec/settings.ini
  * Windows: %LOCALAPPDATA%/radiorec/settings.ini
  * copy the settings.ini next to the script
  * use the commandline option '-s' to specify custom path to the settings file.
3. Adjust the settings to your needs. You can happily add more radio stations to the STATIONS section. **Check at least the the WebDav Section**

# Usage
## As Script
Open a shell and go to the directory where radiorec.py is located.
General usage:
* Windows: py radiorec.py
* Linux: python3 radiorec.py OR JUST ./radiorec.py

What you want to do first is getting some help about how to use the scipt:
./radiorec.py --help
or get some help for the record command:
./radiorec.py record --help

There are two main commands: record and list.

Recording a radio station usually works as follows:
./radiorec.py record <station> <duration> [name]
<station> is the radio station name, for example: dlf
<duration> is how long the recording runs in minutes, for example: 60
[name] is not required and is (currently) just appended to the filename.
Thus the command line is:
./radiorec.py record dlf 60 mytest

You can get a list of all known radio stations with:
./radiorec.py list
You can edit/add the radio stations in the STATIONS section of the settings
file.

##Docker
Please note that the Docker-Container may not have the same time as your host!
**To Do**

#Known problems
The Windows command line (cmd and powershell) still has problems with UTF-8.
Using the --verbose option might cause the script to crash with an
UnicodeEncodeError. If you want to avoid the crash, you have to do both,
change the command line codepage and the font. For example, doing a
"chcp 65001" and changing the font to "Lucidia Console" should help.

#Acknowledgements
The main work is from the radiorec project by beedaddy (https://github.com/beedaddy/radiorec).

This project got inspiration from the dradio project by prometoys
(https://github.com/prometoys/dradio). Thanks for that!

--
If you have any questions or suggestions (or bug reports!), feel free to use
the github issue tracker: https://github.com/WhiteTomX/radiorecwebdav
