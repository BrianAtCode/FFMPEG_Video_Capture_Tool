import tkinter as tk

# Import frame classes
from capture_frame import CaptureFrame
from video_edit_frame import VideoEditFrame

class VideoCaptureTool:
    def __init__(self, root):
        self.root = root
        self.root.title("FFMPEG Stream Capture Tool")
        self.root.resizable(False, False)
        self.root.geometry("1250x700")

        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)

        # Create side navigation
        self.side_nav = tk.Frame(self.main_container, width=200, bg='#2c3e50')
        self.side_nav.pack(side='left', fill='y')
        self.side_nav.pack_propagate(False)

        # Create content area
        self.content_area = tk.Frame(self.main_container)
        self.content_area.pack(side='left', fill='both', expand=True)

        # Create frame container for switchable frames
        self.frame_container = tk.Frame(self.content_area)
        self.frame_container.pack(fill='both', expand=True)
        self.frame_container.place(relx=0.5, rely=0.5, anchor='center')

        # Initialize frames dictionary and tasks
        self.frames = {}

        # Setup frames
        self.setup_frames()
        self.setup_nav_buttons()
        self.show_frame('capture')

    def setup_nav_buttons(self):
        # Style for nav buttons
        style = {
            'width': 20,
            'height': 2,
            'bg': '#2c3e50',
            'fg': 'white',
            'relief': 'flat',
            'font': ('Arial', 10, 'bold')
        }
        
        # Capture button
        tk.Button(
            self.side_nav,
            name="capture",
            text="Stream Capture",
            command=lambda: self.show_frame('capture'),
            **style
        ).pack(pady=5)
        
        # Edit button
        tk.Button(
            self.side_nav,
            name="edit",
            text="Video Editor",
            command=lambda: self.show_frame('edit'),
            **style
        ).pack(pady=5)

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        self.frames[frame_name].pack(fill='both', expand=True)

        # reset the text color and background color of all buttons
        for item in self.side_nav.children:
            self.side_nav.children[item].config(bg='#2c3e50', fg='white')

        # change the text color and background color of the selected button
        self.side_nav.children[frame_name].config(bg='#3498db', fg='white')

    def setup_frames(self):
        # Pass the shared tasks dictionary to both frames
        self.frames['capture'] = CaptureFrame(self.frame_container)
        self.frames['edit'] = VideoEditFrame(self.frame_container)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCaptureTool(root)
    root.mainloop()

