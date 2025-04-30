#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog
import vlc

class Player():
    def __init__(self, tk_root):
        # Initialize objects
        self.root = tk_root
        self.root.title("Audio Player")
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        # Create play/pause button
        self.play_button = tk.Button(root, text="Play/Pause", command=self.pause)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create stop button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Create volume slider
        self.volume_slider = tk.Scale(root, from_=0, to=100, orient="vertical", command=self.set_volume)
        self.volume_slider.pack(side=tk.LEFT, padx=5, pady=5)
        # Create position slider
        self.pos = tk.DoubleVar()
        self.pos_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", variable = self.pos, command=self.set_position)
        self.pos_slider.pack(fill=tk.X, padx=10, pady=5)
        # Create open file button
        self.file_button = tk.Button(root, text="Open File", command=self.open_file)
        self.file_button.pack(side=tk.LEFT, padx=5, pady=5)

    def open_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.player.set_media(self.instance.media_new(file_path))
            self.player.play()

    def pause(self):
        self.player.pause()

    def play(self):
        self.player.play()

    def stop(self):
        self.player.stop()

    def set_position(self, position):
        self.player.set_position(float(position) / 100)

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume))

    def update_sliders(self):
        self.pos.set(float(self.player.get_position() * 100))
        self.root.after(1000, self.update_sliders)
# player = Player(sys.argv[0])
# player.vlc.play()

if __name__ == "__main__":
    root = tk.Tk()
    player = Player(root)
    player.root.after(100, player.update_sliders)
    root.mainloop()