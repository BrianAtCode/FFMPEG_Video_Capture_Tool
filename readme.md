# FFMPEG Video Capture Tool

## About
FFMPEG Video Capture Tool is a desktop application that provides two main functionalities:
- Stream Capture: Allows users to capture video streams from URLs using FFMPEG
- Video Editor: Enables users to edit and splice video files with precise time intervals

The tool features a user-friendly interface with a side navigation panel for switching between capture and edit modes, making video processing tasks simple and efficient.

## Download & Setup

### Step 1: FFMPEG & FFprobe Installation
1. Download FFMPEG from the official website: https://ffmpeg.org/download.html (included in FFMPEG package)
2. Extract the downloaded zip file
3. Add FFMPEG to Windows Environment Path:
   - Open System Properties > Advanced > Environment Variables
   - Under System Variables, find and select "Path"
   - Click "Edit" and add the path to FFMPEG's bin folder
   - Click "OK" to save changes

### Step 2: Get the Application
Choose one of these options:

Option 1: Download Released Version
- Download the latest release from: https://github.com/BrianAtCode/FFMPEG_Video_Capture_Tool/releases/tag/production

Option 2: Build from Source
- Install PyInstaller: `pip install pyinstaller`
- Run command: `pyinstaller --noconsole --onedir FFMPEG_Video_Capture_Tool.py`
- Find the executable in the generated 'dist' folder

## Operating System
- Currently supports Windows operating systems only