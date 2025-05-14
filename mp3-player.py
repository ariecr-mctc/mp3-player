#!/usr/bin/env python3
from threading import Thread
import tkinter as tk
from tkinter import filedialog, simpledialog
import vlc
import yt_dlp


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.mlistplayer = self.instance.media_list_player_new()
        self.mplayer = self.mlistplayer.get_media_player()
        self.events = self.mplayer.event_manager()
        # Initialize YT-DLP before usage to slightly reduce loading times
        # Opts explanation: Get the best audio, don't actually download playlist
        ydl_opts = {'format': 'bestaudio', 'extract_flat': 'in_playlist'}
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.ydl_url = None
        self.ydl_thread = None

    def get_position(self):
        return self.mplayer.get_position()

    def next(self):
        self.mlistplayer.next()

    def open(self, uri):
        mlist = self.instance.media_list_new()
        if uri.startswith('http'):
            # Get raw audio URL and metadata with yt-dlp. May not work if YouTube breaks something.
            self.ydl_url = uri
            yt_info = self.ydl.extract_info(uri, download=False)
            if yt_info:
                try:  # Try extracting playlist
                    song_list = yt_info['entries']
                    # Download the first item so we have something to give to VLC
                    yt_info = self.ydl.extract_info(song_list[0]['url'], download=False)
                    media = self.instance.media_new(yt_info['url'])
                    media.set_meta(vlc.Meta.Title, yt_info['title'])
                    mlist.add_media(media)
                    self.ydl_thread = Thread(target=self._ydl_background_thread, args=(mlist, song_list, self.mlistplayer))
                    self.ydl_thread.start()
                except KeyError:  # Single song
                    media = self.instance.media_new(yt_info['url'])
                    media.set_meta(vlc.Meta.Title, yt_info['title'])
                    mlist.add_media(media)
        else:
            # Parse metadata
            media = self.instance.media_new(uri)
            vlc.libvlc_media_parse_with_options(media, vlc.MediaParseFlag(network=True), 5000)
            mlist.add_media(media)
        # Play the media with VLC
        self.mlistplayer.set_media_list(mlist)
        self.mlistplayer.play()

    def pause(self):
        self.mlistplayer.pause()

    def prev(self):
        self.mlistplayer.previous()

    def save(self, path):
        ydl_opts = {'format': 'bestaudio',
                    'postprocessors': [{
                    # Embed metadata
                        'key': 'FFmpegMetadata',
                        'add_chapters': True,
                        'add_metadata': True,
                        'add_infojson': 'if_exists'
                    }, {
                        'key': 'SavePlaylist'
                    }, {
                    # Remove characters from file name that VLC doesn't like
                        'actions': [(yt_dlp.postprocessor.metadataparser.MetadataParserPP.replacer,
                            'title',
                            '#',
                            '_')],
                        'key': 'MetadataParser',
                        'when': 'pre_process'},
                    ],
                    'overwrites': True,
                    # Output template
                    'outtmpl': f'{path}/%(uploader)s - %(title)s.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.ydl_url)

    def stop(self):
        self.mlistplayer.stop()

    def set_position(self, position):
        self.mplayer.set_position(position)

    def set_volume(self, volume):
        self.mplayer.audio_set_volume(int(volume))

    def _ydl_background_thread(self, mlist, song_list, mlistplayer):
        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for song in song_list[1:50]:  # Skip first song, we already have it. Also limit to 50 songs to not get temp banned by YT.
                url = song['url']  # Extract each URL from the playlist one at a time
                yt_info = self.ydl.extract_info(url, download=False)
                # Get real media URL and feed it to VLC
                media = self.instance.media_new(yt_info['url'])
                media.set_meta(vlc.Meta.Title, yt_info['title'])
                mlist.add_media(media)



class PlayerGui:
    def __init__(self, tk_root, player=Player()):
        # Initialize objects
        self.root = tk_root
        self.root.title('Audio Player')
        self.root.columnconfigure(3, weight=1)
        self.root.minsize(750, 100)
        self.player = player
        self.player.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.clear_current)
        self.player.events.event_attach(vlc.EventType.MediaPlayerPlaying, self.set_needs_update)
        # Update media info
        self.media_needs_update = False
        self.job = self.root.after(100, self.update_media_info)
        # Create play/pause button
        self.play_button = tk.Button(self.root, text='Play/Pause', command=self.player.pause)
        self.play_button.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        # Create stop button
        self.stop_button = tk.Button(self.root, text='Stop', command=self.stop)
        self.stop_button.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
        # Create open file button
        self.file_button = tk.Button(self.root, text='Open File', command=self.open_file)
        self.file_button.grid(row=1, column=0, sticky='nsew', padx=2, pady=2)
        # Create open URL button
        self.url_button = tk.Button(self.root, text='Open URL', command=self.open_url)
        self.url_button.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)
        # Create save button
        self.save_button = tk.Button(self.root, text='Save As', command=self.save_media)
        self.save_button.grid(row=2, column=0, columnspan=2, sticky='ns', padx=2, pady=2)
        # Create volume slider
        self.volume_slider = tk.Scale(self.root, from_=100, to=0, orient='vertical', command=self.player.set_volume)
        self.volume_slider.set(100)
        self.volume_slider.grid(row=0, column=2, rowspan=3)
        self.volume_label = tk.Label(self.root, text='Volume')
        self.volume_label.grid(row=3, column=2, sticky='n')
        # Create media display
        self.now_playing_text = tk.StringVar(value='Now Playing: N/A')
        self.now_playing = tk.Label(self.root, textvariable=self.now_playing_text)
        self.now_playing.grid(row=1, column=3, columnspan=4, sticky='nsew')
        # Create position slider
        self.pos_slider = tk.Scale(self.root, from_=0, to=100, orient='horizontal', showvalue=False)
        self.pos_slider.bind('<ButtonPress-1>', self.cancel_job)  # Avoid slider position updating while scrubbing
        self.pos_slider.bind('<ButtonRelease-1>', self.set_position)  # Avoid constant audio clipping when scrubbing
        self.pos_slider.grid(row=2, column=3, columnspan=4, sticky='nsew', padx=10)
        self.prev_button = tk.Button(self.root, text='<==', command=self.player.prev)
        self.prev_button.grid(row=3, column=3, sticky='nsw', padx=2, pady=2)
        self.next_button = tk.Button(self.root, text='==>', command=self.player.next)
        self.next_button.grid(row=3, column=6, sticky='nsew', padx=2, pady=2)

    # Disable slider updates while scrubbing
    def cancel_job(self, event=None):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def clear_current(self, event=None):  # VLC event callback
        self.now_playing_text.set('Now Playing: N/A')

    def open_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.open_media(file_path)

    def open_media(self, url):
        self.player.open(url)
        # Fix volume not applying on media start
        self.player.set_volume(self.volume_slider.get())

    def open_url(self):
        url = tk.simpledialog.askstring('Open URL', 'Enter the URL to play:')
        if url:
            self.player.stop()
            # Set now playing text to be more descriptive
            self.now_playing_text.set('YT-DLP is fetching media, please wait...')
            self.root.update()
            self.open_media(url)

    def save_media(self):  # Save last opened YouTube link to directory
        file_path = tk.filedialog.askdirectory()
        if file_path:
            save_thread = Thread(target=self.player.save, args=(file_path,))
            save_thread.start()

    def set_needs_update(self, event=None):  # VLC event callback
        self.media_needs_update = True

    def set_position(self, event=None):
        self.player.set_position(float(self.pos_slider.get()) / 100)
        self.job = self.root.after(1000, self.update_media_info)  # Re-enable progress bar updates

    def stop(self):
        self.player.stop()
        self.clear_current()

    def update_media_info(self):
        self.pos_slider.set(self.player.get_position() * 100)
        if self.media_needs_update:  # VLC callbacks are not reentrant
            title = self.player.mplayer.get_media().get_meta(vlc.Meta.Title)
            if title is not None:  # Set now playing text, or a fallback message in case of errors
                self.now_playing_text.set('Now Playing: ' + title)
            else:
                self.now_playing_text.set('Error: Media info not found.')
            self.media_needs_update = False
        self.job = self.root.after(200, self.update_media_info)


if __name__ == '__main__':
    root = tk.Tk()
    playergui = PlayerGui(root)
    root.mainloop()
