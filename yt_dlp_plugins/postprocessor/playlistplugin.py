# Plugin that creates an m3u playlist of the downloaded videos in the order
# they are downloaded. The m3u is named after the playlist and put in the
# output directory.

import os
# ⚠ Don't use relative imports
from yt_dlp.postprocessor.common import PostProcessor

# See the docstring of yt_dlp.postprocessor.common.PostProcessor
class SavePlaylistPP(PostProcessor):
    def __init__(self, downloader=None, **kwargs):
        # ⚠ Only kwargs can be passed from the CLI, and all argument values will be string
        # Also, "downloader", "when" and "key" are reserved names
        super().__init__(downloader)
        self._kwargs = kwargs

    # See docstring of yt_dlp.postprocessor.common.PostProcessor.run
    def run(self, info):
        title = info.get('playlist_title', 'playlist')
        if info.get('_type', 'video') != 'video':  # PP was called for playlist
            self.to_screen(f'Post-processing playlist {info.get("id")!r} with {self._kwargs}')
            self.report_warning("PP was called for playlist -- not supported")
        elif info.get('filepath'):  # PP was called after download (default)
            filepath = info.get('filepath')
            self.to_screen(f'Post-processed {filepath!r} with {self._kwargs}')
            self.append_to_playlist_file(title, filepath)
        elif info.get('requested_downloads'):  # PP was called after_video
            filepaths = [f.get('filepath') for f in info.get('requested_downloads')]
            self.to_screen(f'Post-processed {filepaths!r} with {self._kwargs}')
            for filepath in filepaths:
                self.append_to_playlist_file(title, filepath)
        else:  # PP was called before actual download
            filepath = info.get('_filename')
            self.to_screen(f'Pre-processed {filepath!r} with {self._kwargs}')
            self.append_to_playlist_file(title, filepath)
        return [], info  # return list_of_files_to_delete, info_dict

    def append_to_playlist_file(self, title, filepath):
        playlist_path = os.path.join(os.path.dirname(filepath), f'{title}.m3u')
        with open(playlist_path, 'a+') as file:
            file.write(os.path.basename(filepath)) # make sure paths are relative to the output dir
            file.write("\n")