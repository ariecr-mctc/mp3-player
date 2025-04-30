#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, simpledialog
import vlc
import yt_dlp


class Player():
    def __init__(self):
        self.instance = vlc.Instance()
        self.mplayer = self.instance.media_player_new()

    def get_position(self):
        return self.mplayer.get_position()

    def open(self, uri):
        if uri.startswith('http'):
            # Get raw audio URL with yt-dlp. May not work if YouTube breaks something.
            ydl_opts = {'format': 'bestaudio'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(uri, download=False)
            if song_info:
                uri = song_info['url']
        # Open media with VLC
        self.mplayer.set_media(self.instance.media_new(uri))
        self.mplayer.play()

    def pause(self):
        self.mplayer.pause()

    def play(self):
        self.mplayer.play()

    def stop(self):
        self.mplayer.stop()

    def set_position(self, position):
        self.mplayer.set_position(position)

    def set_volume(self, volume):
        self.mplayer.audio_set_volume(int(volume))


class PlayerGui():
    def __init__(self, tk_root, player=Player()):
        # Initialize objects
        self.root = tk_root
        self.root.title('Audio Player')
        self.player = player
        # Update sliders
        self.job = self.root.after(100, self.update_sliders)
        # Create play/pause button
        self.play_button = tk.Button(root, text='Play/Pause', command=self.player.pause)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create stop button
        self.stop_button = tk.Button(root, text='Stop', command=self.player.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create volume slider
        self.volume_slider = tk.Scale(root, from_=100, to=0, orient='vertical', command=self.player.set_volume, label='Volume')
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.LEFT, padx=5, pady=5)
        # Create position slider
        self.pos_slider = tk.Scale(root, from_=0, to=100, orient='horizontal')
        self.pos_slider.bind('<ButtonPress-1>', self.cancel_job)  # Avoid slider position updating while scrubbing
        self.pos_slider.bind('<ButtonRelease-1>', self.set_position)  # Avoid constant audio clipping when scrubbing
        self.pos_slider.pack(fill=tk.X, padx=10, pady=5)
        # Create open file button
        self.file_button = tk.Button(root, text='Open File', command=self.open_file)
        self.file_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create open URL button
        self.url_button = tk.Button(root, text='Open URL', command=self.open_url)
        self.url_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Disable slider updates while scrubbing
    def cancel_job(self, event=None):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def open_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.player.open(file_path)

    def open_url(self):
        url = tk.simpledialog.askstring('Open URL', 'Enter the URL to play:')
        self.player.open(url)

    def set_position(self, event=None):
        self.player.set_position(float(self.pos_slider.get()) / 100)
        self.job = self.root.after(1000, self.update_sliders)  # Re-enable progress bar updates

    def update_sliders(self):
        self.pos_slider.set(self.player.get_position() * 100)
        self.job = self.root.after(1000, self.update_sliders)


if __name__ == '__main__':
    root = tk.Tk()
    playergui = PlayerGui(root)
    root.mainloop()
