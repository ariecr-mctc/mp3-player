#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, simpledialog
import vlc
import yt_dlp


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.mplayer = self.instance.media_player_new()
        self.events = self.mplayer.event_manager()
        # Initialize YT-DLP before usage to reduce loading times
        ydl_opts = {'format': 'bestaudio'}
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.ydl_url = None

    def get_position(self):
        return self.mplayer.get_position()

    def open(self, uri):
        media = None
        title = None
        if uri.startswith('http'):
            # Get raw audio URL and metadata with yt-dlp. May not work if YouTube breaks something.
            self.ydl_url = uri
            song_info = self.ydl.extract_info(uri, download=False)
            if song_info:
                media = self.instance.media_new(song_info['url'])
                title = song_info['title']
        else:
            # Parse metadata
            media = self.instance.media_new(uri)
            vlc.libvlc_media_parse_with_options(media, vlc.MediaParseFlag(network=True), 5000)
            # Above method is asynchronous, wait until done
            while not vlc.libvlc_media_get_parsed_status(media):
                continue
            title = media.get_meta(vlc.Meta.Title)
        # Play the media with VLC
        self.mplayer.set_media(media)
        self.mplayer.play()
        return title

    def pause(self):
        self.mplayer.pause()

    def play(self):
        self.mplayer.play()

    def save(self, path):
        ydl_opts = {'format': 'bestaudio', 'outtmpl': f'{path}.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.ydl_url)

    def stop(self):
        self.mplayer.stop()

    def set_position(self, position):
        self.mplayer.set_position(position)

    def set_volume(self, volume):
        self.mplayer.audio_set_volume(int(volume))


class PlayerGui:
    def __init__(self, tk_root, player=Player()):
        # Initialize objects
        self.root = tk_root
        self.root.title('Audio Player')
        self.root.columnconfigure(3, weight=1)
        self.root.minsize(600, 100)
        self.player = player
        # Update sliders
        self.job = self.root.after(100, self.update_sliders)
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
        self.save_button = tk.Button(self.root, text='Save File', command=self.save_file)
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
        self.now_playing.grid(row=1, column=3, sticky='nsew')
        # Create position slider
        self.pos_slider = tk.Scale(self.root, from_=0, to=100, orient='horizontal', showvalue=False)
        self.pos_slider.bind('<ButtonPress-1>', self.cancel_job)  # Avoid slider position updating while scrubbing
        self.pos_slider.bind('<ButtonRelease-1>', self.set_position)  # Avoid constant audio clipping when scrubbing
        self.pos_slider.grid(row=2, column=3, sticky='nsew', padx=10)

    # Disable slider updates while scrubbing
    def cancel_job(self, event=None):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def open_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.open_media(file_path)

    def open_media(self, url):
        title = self.player.open(url)
        # Fix volume not applying on media start
        self.player.set_volume(self.volume_slider.get())
        # Set now playing text, or a fallback message in case of errors
        if title is not None:
            self.now_playing_text.set('Now Playing: ' + title)
        else:
            self.now_playing_text.set('Error: Media info not found.')

    def open_url(self):
        url = tk.simpledialog.askstring('Open URL', 'Enter the URL to play:')
        if url:
            self.player.stop()
            # Set now playing text to be more descriptive
            self.now_playing_text.set('YT-DLP is fetching media, please wait...')
            self.root.update()
            self.open_media(url)

    def save_file(self):
        file_path = tk.filedialog.asksaveasfilename()
        self.player.save(file_path)

    def set_position(self, event=None):
        self.player.set_position(float(self.pos_slider.get()) / 100)
        self.job = self.root.after(1000, self.update_sliders)  # Re-enable progress bar updates

    def stop(self):
        self.player.stop()
        self.now_playing_text.set('Now Playing: N/A')

    def update_sliders(self):
        self.pos_slider.set(self.player.get_position() * 100)
        self.job = self.root.after(1000, self.update_sliders)


if __name__ == '__main__':
    root = tk.Tk()
    playergui = PlayerGui(root)
    root.mainloop()
