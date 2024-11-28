import os
from pathlib import Path
import asyncio
import json
import threading

# import demuxer type for the input file
from DEMUXER_TYPES import DEMUXER_TYPES

class MediaInfo:
    def __init__(self, filepath):
        self.filepath = filepath
        self.type = None
        self.duration = None
        self.size = None
        self.acodec = None
        self.vcodec = None
        self.content_type = None
    
    def check_file(self):
        extension = None
        if self.is_url(self.filepath):
            # get the file extension from the URL
            extension = self.filepath.split('.')[-1]
        elif os.path.exists(self.filepath):
            extension = Path(self.filepath).suffix.lower().lstrip('.')
            self.filepath = str(Path(self.filepath).resolve())
            print(f"File {self.filepath} exist.")
        else:
            print(f"File {self.filepath} does not exist.")
            return False
        
        probe_data = asyncio.run(self.get_metadata())

        if self.has_meta_column('format', probe_data):
            self.type = self.get_file_type(extension, self.has_meta_column('format_name', probe_data['format']))
            self.duration = self.get_media_duration(self.has_meta_column('duration', probe_data['format']))
            self.size = self.get_media_size(self.has_meta_column('size', probe_data['format']))
        
        if self.has_meta_column('streams', probe_data):
            self.acodec = self.get_media_codec(probe_data['streams'], 'audio') if self.acodec is None else self.acodec
            self.vcodec = self.get_media_codec(probe_data['streams'], 'video') if self.vcodec is None else self.vcodec
        return True

    def has_meta_column(self, name, partition):
        if name in partition:
            return partition[name]
        else:
            return None

    def return_json(self, func):
        t = threading.Thread(target=self.return_json_thread, args=(func,))
        t.start()
    
    def return_json_thread(self, func):
        if self.check_file():
            return func(True, {
                'filepath': self.filepath,
                'type': self.type,
                'duration': self.duration,
                'size': self.size,
                'acodec': self.acodec,
                'vcodec': self.vcodec
            })
        else:
            return func(False, {})
    
    def get_json(self):
        return {
            'filepath': self.filepath,
            'type': self.type,
            'duration': self.duration,
            'size': self.size,
            'acodec': self.acodec,
            'vcodec': self.vcodec
        }

    def is_url(self, path):
        return path.startswith(('http://', 'https://', 'ftp://', 'sftp://'))

    async def get_metadata(self):
        cmd = f'ffprobe -v quiet -show_format -show_streams -print_format json "{self.filepath}"'
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Error: {stderr.decode().strip()}")
            return {}
            
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {}

    def get_file_type(self, file_extension, format_name):
        if format_name is None:
            return None
        
        try:
            # Check against cached muxer types
            for mtype, formats in DEMUXER_TYPES.items():
                if any(fmt in format_name for fmt in formats):
                    return mtype
                
                # Also check extension
                if file_extension in formats:
                    return mtype
                
        except Exception as e:
            print(f"Error analyzing file: {e}")
        
        return "unknown"
    
    def get_media_duration(self, duration):
        if self.duration is not None:
            return self.duration

        if duration is None:
            return None
        
        # change the duration format from 00.00 second to 00:00:00
        hours = int(float(duration) // 3600)
        minutes = int((float(duration) % 3600) // 60)
        seconds = int(float(duration) % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    
    def get_media_size(self, size):
        if self.size is not None:
            return self.size
        
        if size is None:
            return None
        
        # Define size units and thresholds
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        # Round to 2 decimal places
        return f"{size:.2f} {units[unit_index]}"
    
    def get_media_codec(self, streams, type):
        if streams is None:
            return None
         
        audio_streams = [stream['codec_name'] for stream in streams if stream['codec_type'] ==  type]
        
        if len(audio_streams) == 0:
            return None
        # join the list of audio codecs into a single string and return it
        return ', '.join(audio_streams)