mp3-player
=========
Basic Audio Player Written in Python using Tk, libvlc and yt-dlp

Prerequisites
--------------
- You need to have VLC media player installed on your system.  
- Metadata embedding in downloaded files will not work without FFmpeg in your PATH.  
- YT-DLP specific FFmpeg builds can be found here https://github.com/yt-dlp/FFmpeg-Builds. Download the static linked binaries if you're not sure which one to use, they should work if placed in the same directory as the script.

Installation
--------------
```
git clone https://github.com/ariecr-mctc/mp3-player.git
cd mp3-player
pip install -r requirements.txt
```

Usage
--------------
Run mp3-player.py

TODO
--------------
- Open filename given as an arg on cmdline
- Add playlist support

Stretch Goals
--------------
- Add album art preview
- Add m3u8 playlist support

Credits
--------------
https://codeloop.org/how-to-build-media-player-in-python-tkinter/