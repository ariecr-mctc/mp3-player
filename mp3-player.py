#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, simpledialog
import vlc
import yt_dlp


class Player():
    def __init__(self, tk_root):
        # Initialize objects
        self.root = tk_root
        self.root.title('Audio Player')
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        # Update sliders
        self.job = self.root.after(100, self.update_sliders)
        # Create play/pause button
        self.play_button = tk.Button(root, text='Play/Pause', command=self.pause)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create stop button
        self.stop_button = tk.Button(root, text='Stop', command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create volume slider
        self.volume_slider = tk.Scale(root, from_=100, to=0, orient='vertical', command=self.set_volume, label='Volume')
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
            self.player.set_media(self.instance.media_new(file_path))
            self.player.play()

    def open_url(self):
        url = tk.simpledialog.askstring('Open URL', 'Enter the URL to play:')
        # Get raw audio URL with yt-dlp. May not work if YouTube breaks something.
        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(url, download=False)
        if song_info:
            real_url = song_info['url']
            self.player.set_media(self.instance.media_new(real_url))
            self.player.play()

    def pause(self):
        self.player.pause()

    def play(self):
        self.player.play()

    def stop(self):
        self.player.stop()
    def set_position(self, event=None):
        self.player.set_position(float(self.pos_slider.get()) / 100)
        self.job = self.root.after(1000, self.update_sliders) # Re-enable progress bar updates

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume))

    def update_sliders(self):
        self.pos_slider.set(self.player.get_position() * 100)
        self.job = self.root.after(1000, self.update_sliders)


# player = Player(sys.argv[0])
# player.vlc.play()

if __name__ == '__main__':
    root = tk.Tk()
    player = Player(root)
    root.mainloop()
