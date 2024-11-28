import re
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import os
import queue
import time
from Media_Info import MediaInfo
from Ticket import Ticket,TicketPurpose

class VideoEditFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_copy_profile = tk.BooleanVar()
        self.setup_edit_interface()
        self.setup_data_table()
        self.tasks = {}
        self.current_process_id = ""
        self.interval_window_open = False
        self.bind("<<CheckEditQueue>>", self.check_queue)
        self.queue_message = queue.Queue()
        self.bind("<<UpdateProgressTime>>", self.update_progress)
        self.time_queue = queue.Queue()

    def update_progress(self, event):
        msg: Ticket
        msg = self.time_queue.get()

        if msg.ticket_type == TicketPurpose.UI_TABLE_PROGRESS:
            self.update_data_table_progress(msg.ticket_id, msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_PROGRESS:
            self.progress_time_label.config(text=msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_CONVERSION_TIME:
            self.conversion_time_label.config(text=msg.ticket_value)
        else:
            if msg.ticket_id == "" or msg.ticket_id not in self.tasks:
                return
            self.tasks[msg.ticket_id][msg.ticket_type.value] = msg.ticket_value
    
    def check_queue(self, event):
        msg: Ticket
        msg = self.queue_message.get()
        #print(f"Processing event at {time.time()} type: {msg.ticket_type}")
        if msg.ticket_type == TicketPurpose.UI_TABLE_STATUS:
            #print(time.time(),": ",msg.ticket_id,'-',msg.ticket_type, "-", msg.ticket_value)
            self.update_data_table_status(msg.ticket_id, msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_INPUT_PATH:
            self.input_path_label.config(text=msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_INPUT_VCORDEC:
            self.input_vcodec_label.config(text=msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_INPUT_ACODEC:
            self.input_acodec_label.config(text=msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_VIDEO_LENGTH:
            self.video_length_label.config(text=msg.ticket_value)
        else:
            if msg.ticket_id == "" or msg.ticket_id not in self.tasks:
                return
            
            self.tasks[msg.ticket_id][msg.ticket_type.value] = msg.ticket_value


    def setup_edit_interface(self):
        # Add video editing UI components here
        # This is where you build your video editing interface
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(frame, text="Id:").grid(row=0, column=0, sticky='w')
        self.id_label = tk.Label(frame, text="1")
        self.id_label.grid(row=0, column=1, sticky='w')
        
        tk.Label(frame, text="Video file Path:").grid(row=1, column=0, sticky='w')
        self.input_path_label = tk.Label(frame, text="Not Set")
        self.input_path_label.grid(row=1, column=1, sticky='w')
        self.set_file_button = tk.Button(frame, text="Set File", command=self.set_video_file)
        self.set_file_button.grid(row=1, column=2)

        tk.Label(frame, text="Input Video codec:").grid(row=2, column=0, sticky='w')
        self.input_vcodec_label = tk.Label(frame, text="Unknown")
        self.input_vcodec_label.grid(row=2, column=1, sticky='w')
        
        tk.Label(frame, text="Input Audio codec:").grid(row=3, column=0, sticky='w')
        self.input_acodec_label = tk.Label(frame, text="Unknown")
        self.input_acodec_label.grid(row=3, column=1, sticky='w')
        
        tk.Label(frame, text="Video Output Name:").grid(row=4, column=0, sticky='w')
        self.name_entry = tk.Entry(frame, width=50)
        self.name_entry.grid(row=4, column=1)

        tk.Label(frame, text="Output Path:").grid(row=5, column=0, sticky='w')
        self.output_path_label = tk.Label(frame, text="Not Set")
        self.output_path_label.grid(row=5, column=1, sticky='w')
        self.set_folder_button = tk.Button(frame, text="Set Folder", command=self.set_output_folder)
        self.set_folder_button.grid(row=5, column=2)

        tk.Label(frame, text="Output Type:").grid(row=6, column=0, sticky='w')
        self.output_type_entry = tk.Entry(frame, width=50)
        self.output_type_entry.insert(0, "mp4")
        self.output_type_entry.grid(row=6, column=1)
        
        tk.Label(frame, text="Output Video codec:").grid(row=7, column=0, sticky='w')
        self.output_vcodec_entry = tk.Entry(frame, width=50)
        self.output_vcodec_entry.insert(0, "Unknown")
        self.output_vcodec_entry.grid(row=7, column=1)
        
        tk.Label(frame, text="Output Audio codec:").grid(row=8, column=0, sticky='w')
        self.output_acodec_entry = tk.Entry(frame, width=50, textvariable="Unknown")
        self.output_acodec_entry.insert(0, "Unknown")
        self.output_acodec_entry.grid(row=8, column=1)
        
        tk.Label(frame, text="Status:").grid(row=9, column=0, sticky='w')
        self.status_label = tk.Label(frame, text="Idle")
        self.status_label.grid(row=9, column=1, sticky='w')

        tk.Label(frame, text="Splice Interval:").grid(row=10, column=0, sticky='w')
        self.splice_interval_label = tk.Label(frame, text="00:00:00 - 01:00:00")
        self.splice_interval_label.grid(row=10, column=1, sticky='w')
        self.set_interval_button = tk.Button(frame, text="Set Interval", command=self.show_interval_window)
        self.set_interval_button.grid(row=10, column=2)

        tk.Label(frame, text="Video Length:").grid(row=11, column=0, sticky='w')
        self.video_length_label = tk.Label(frame, text="00:00:00")
        self.video_length_label.grid(row=11, column=1, sticky='w')

        tk.Label(frame, text="Splice Length:").grid(row=12, column=0, sticky='w')
        self.splice_length_label = tk.Label(frame, text="01:00:00")
        self.splice_length_label.grid(row=12, column=1, sticky='w')
        
        tk.Label(frame, text="Progress Time:").grid(row=13, column=0, sticky='w')
        self.progress_time_label = tk.Label(frame, text="00:00:00")
        self.progress_time_label.grid(row=13, column=1, sticky='w')
        
        tk.Label(frame, text="Conversion Time:").grid(row=14, column=0, sticky='w')
        self.conversion_time_label = tk.Label(frame, text="00:00:00")
        self.conversion_time_label.grid(row=14, column=1, sticky='w')

        self.isCopy_checkbox = tk.Checkbutton(frame, text="copy the current profile while creating new profile", 
                                              variable=self.is_copy_profile, 
                                              command=self.retain_profile)
        self.isCopy_checkbox.grid(row=15, column=0, columnspan=2, sticky='w')

        task_button_group = tk.Frame(frame)
        task_button_group.grid(row=16, column=0, columnspan=3, sticky='ew')

        tk.Button(task_button_group, text="Create profile", command=self.create_profile).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.start_button = tk.Button(task_button_group, text="Start Edit", command=self.start_editing)
        self.start_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.complete_button = tk.Button(task_button_group, text="Complete", state=tk.DISABLED, command=self.complete_edit)
        self.complete_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.cancel_button = tk.Button(task_button_group, text="Cancel", state=tk.DISABLED, command=self.cancel_edit)
        self.cancel_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        return
    
    def setup_data_table(self):
        # Create data table frame
        self.table_frame = tk.Frame(self)
        self.table_frame.grid(column=0, row=2, sticky='w')
        
        self.tree = ttk.Treeview(self.table_frame, columns=("name", "path", "type", "status","progress"), show='headings')
        self.tree.heading("name", text="Name")
        self.tree.heading("path", text="Path")
        self.tree.heading("type", text="Extension")
        self.tree.heading("status", text="Status")
        self.tree.heading("progress", text="Progress")
        self.tree.grid(column=0, row=0, pady=10, padx=10)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)

    def on_row_click(self, event):
        if len(self.tree.selection()) == 0:
            return
        self.current_process_id = str(self.tree.selection()[0])
        task = self.tasks[self.current_process_id]
        #print(self.current_process_id, task)
        self.id_label.config(text=self.current_process_id)

        self.start_button.config(state=tk.DISABLED)
        if task["status"] == "Success" or task["status"] == "Failed" or task["status"] == "Stopping":
            self.complete_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)
        else:
            self.complete_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)

        self.name_entry.config(state=tk.NORMAL)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, task["name"])
        self.name_entry.config(state=tk.DISABLED)

        self.status_label.config(text=task["status"])

        self.set_file_button.config(state=tk.DISABLED)
        self.input_path_label.config(text=task["input_path"])
        self.input_acodec_label.config(text=task["input_acodec"])
        self.input_vcodec_label.config(text=task["input_vcodec"])

        self.set_folder_button.config(state=tk.DISABLED)
        self.output_path_label.config(text=task["output_path"])

        self.output_type_entry.config(state=tk.NORMAL)
        self.output_type_entry.delete(0, tk.END)
        self.output_type_entry.insert(0, task["output_type"])
        self.output_type_entry.config(state=tk.DISABLED)

        self.output_vcodec_entry.config(state=tk.NORMAL)
        self.output_vcodec_entry.delete(0, tk.END)
        self.output_vcodec_entry.insert(0, task["output_vcodec"])
        self.output_vcodec_entry.config(state=tk.DISABLED)

        self.output_acodec_entry.config(state=tk.NORMAL)
        self.output_acodec_entry.delete(0, tk.END)
        self.output_acodec_entry.insert(0, task["output_acodec"])
        self.output_acodec_entry.config(state=tk.DISABLED)

        interval_full = task["start_time"] + " - " + task["end_time"]
        self.splice_interval_label.config(text=interval_full)
        self.video_length_label.config(text=task["video_length"])
        self.splice_length_label.config(text=task["splice_length"])
        self.progress_time_label.config(text=task["progress_time"])
        self.conversion_time_label.config(text=task["conversion_time"])
        self.set_interval_button.config(state=tk.DISABLED)
        
    
    def start_editing(self):
        self.current_process_id = None
        input_path = self.input_path_label.cget("text") if self.input_path_label.cget("text") != "Not Set" else ""
        output_name = self.name_entry.get()
        output_path = self.output_path_label.cget("text") if self.output_path_label.cget("text") != "Not Set" else ""
        output_type = self.output_type_entry.get()

        # Get splice interval times
        splice_interval = self.splice_interval_label.cget("text")
        start_time, end_time = splice_interval.split(" - ")

        # Get input codecs
        input_vcodec = self.input_vcodec_label.cget("text")
        input_acodec = self.input_acodec_label.cget("text")

        # Get output codecs
        output_vcodec = self.output_vcodec_entry.get()
        output_vcodec = None if output_vcodec == "Unknown" or output_vcodec == "" else output_vcodec

        output_acodec = self.output_acodec_entry.get()
        output_acodec = None if output_acodec == "Unknown" or output_acodec == "" else output_acodec

        # Get video length and splice length
        video_length = self.video_length_label.cget("text")
        splice_length = self.splice_length_label.cget("text")
        progress_time = self.progress_time_label.cget("text")
        conversion_time = self.conversion_time_label.cget("text")

        status = "Editing"
        id = self.create_id()

        #print(f"Starting edit with ID: {id}")
        if not all([input_path, output_name, output_path, output_type]):
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return

        output_file = os.path.join(output_path, f"{output_name}.{output_type}")

        if not self.check_duplicate_filename(output_file):
            return

        # Update the status and data table
        self.status_label.config(text=status)
        self.tasks[id] = {
            "id": id, 
            "name": output_name,
            "input_path": input_path,
            "status": status,
            "output_path": output_path,
            "output_type": output_type,
            "output_file": output_file,
            "input_vcodec": input_vcodec,
            "input_acodec": input_acodec,
            "input_type": None,
            "output_vcodec": output_vcodec,
            "output_acodec": output_acodec,
            "start_time": start_time,
            "end_time": end_time,
            "video_length": video_length,
            "splice_length": splice_length,
            "progress_time": progress_time,
            "conversion_time":conversion_time,
            "process": None
        }

        self.update_data_table(id, output_name, input_path, output_type, status, "0%")
        threading.Thread(target=self.splice_video, 
                         args=(id, input_path, output_file, start_time, end_time, output_vcodec, output_acodec)
                        ).start()

        self.create_profile()

    def send_event(self, id, event_name, event_type, event_data, queue):
        ticket = Ticket(id, event_type, event_data)
        queue.put(ticket)
        self.event_generate(event_name)
        
    def splice_video(self, id, input_path, output_file, start_time, end_time, output_vcodec=None, output_acodec=None):
        command = f'ffmpeg -hide_banner -i "{input_path}" -ss {start_time} -to {end_time}'
        
        if output_vcodec:
            command += f' -c:v {output_vcodec}'
        else:
            command += ' -c:v copy'
        
        if output_acodec:
            command += f' -c:a {output_acodec}'
        else:
            command += ' -c:a copy'
        
        command += f' "{output_file}"'

        # Create process with subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.tasks[id]["process"] = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            shell=True,
            encoding='utf-8'
        )

        output_queue = queue.Queue()

        def process_output():
            try:
                for line in self.tasks[id]["process"].stdout:
                    output_queue.put(line)
            except Exception as e:
                return
            
        # Start output processing thread
        process_thread = threading.Thread(target=process_output)
        process_thread.daemon = True
        process_thread.start()

        process_start_time = time.time()
        def time_to_seconds(time_str):
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        
        video_pattern = r"Video: ([^,]+)"
        audio_pattern = r"Audio: ([^,]+)"
        time_pattern = r"frame=.*time=\s*([0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{2})"
        output_section = False
        while True:
            try:
                current_time = time.time()
                elapsed_process_time = int(current_time - process_start_time)
                hours = elapsed_process_time // 3600
                minutes = (elapsed_process_time % 3600) // 60
                seconds = elapsed_process_time % 60
                timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.send_event(id, "<<UpdateProgressTime>>", TicketPurpose.PROGRESS_TIME, timer_text, self.time_queue)

                if self.current_process_id == id:
                    self.send_event(id, "<<UpdateProgressTime>>", TicketPurpose.UI_FORM_PROGRESS, timer_text, self.time_queue)

                try:
                    line = output_queue.get_nowait()

                    # Process output line
                    time_match = re.search(time_pattern, line)
                    if time_match:
                        elapsed_time = time_match.group(1)
                        if '.' in elapsed_time:
                            elapsed_time = elapsed_time.split('.')[0]
                                                
                        elapsed_seconds = time_to_seconds(elapsed_time)
                        total_seconds = time_to_seconds(self.tasks[id]["splice_length"])
                        percentage = int((elapsed_seconds / total_seconds) * 100)

                        self.send_event(id, "<<UpdateProgressTime>>", TicketPurpose.UI_TABLE_PROGRESS, f"{percentage}%", self.time_queue)
                        self.send_event(id, "<<UpdateProgressTime>>", TicketPurpose.CONVERSION_TIME, elapsed_time, self.time_queue)
                        if self.current_process_id == id:
                            self.send_event(id, "<<UpdateProgressTime>>", TicketPurpose.UI_FORM_CONVERSION_TIME, elapsed_time, self.time_queue)
                            
                    if "Output #0" in line:
                        output_section = True

                    if output_section:
                        video_match = re.search(video_pattern, line)
                        audio_match = re.search(audio_pattern, line)
                        if video_match:
                            output_vcodec_info = video_match.group(1)
                            self.send_event(id, "<<CheckEditQueue>>", TicketPurpose.OUTPUT_VIDEO_CODEC, output_vcodec_info.split(" ")[0], self.queue_message)

                            #self.tasks[id]["output_vcodec"] = output_vcodec_info.split(" ")[0]
                        if audio_match:
                            output_acodec_info = audio_match.group(1)
                            self.send_event(id, "<<CheckEditQueue>>", TicketPurpose.OUTPUT_AUDIO_CODEC, output_acodec_info.split(" ")[0], self.queue_message)
                            #self.tasks[id]["output_acodec"] = output_acodec_info.split(" ")[0]

                except queue.Empty:
                    # Check if process has ended
                    if self.tasks[id]["process"].poll() is not None:
                        if self.tasks[id]["process"].returncode == 0:
                            self.send_event(id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Success", self.queue_message)
                            return
                        else:
                            self.send_event(id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
                        break
                    pass
            except Exception as e:
                #print(f"Error: {traceback.format_exc()}")
                self.send_event(id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
                break

    def update_data_table(self, id, name, input_path, output_type, status, progress_time):
        self.tree.insert("", "end", id=id, values=(name, input_path, output_type, status, progress_time))
    
    def media_info(self, status, info):
        if status:
            self.send_event("", "<<CheckEditQueue>>", TicketPurpose.UI_FORM_INPUT_PATH, info['filepath'], self.queue_message)
            self.send_event("", "<<CheckEditQueue>>", TicketPurpose.UI_FORM_INPUT_VCORDEC, info['vcodec'], self.queue_message)
            self.send_event("", "<<CheckEditQueue>>", TicketPurpose.UI_FORM_INPUT_ACODEC, info['acodec'], self.queue_message)
            self.send_event("", "<<CheckEditQueue>>", TicketPurpose.UI_FORM_VIDEO_LENGTH, info['duration'], self.queue_message)
        else:
            messagebox.showerror("Error", "Invalid video file.")
    
    def set_video_file(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv")])
        if file_path:           
            MediaInfo(file_path).return_json(self.media_info)

    def set_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path_label.config(text=folder)

    def update_data_table_status(self, id, status):
        self.tasks[id]["status"] = status
        
        self.tree.item(id, values=(self.tasks[id]["name"], self.tasks[id]["input_path"], self.tasks[id]["output_type"], status,  self.tree.item(id)['values'][4]))
        self.tree.update()
    
    def update_data_table_progress(self, id, percentage):
        self.tree.item(id, values=(self.tasks[id]["name"], self.tasks[id]["input_path"], self.tasks[id]["output_type"], self.tasks[id]["status"], percentage))
        self.tree.update()
        
    def create_id(self):
        return "1" if len(self.tasks) == 0 else str(int(max(self.tasks))+1)
    
    def create_profile(self):
        self.current_process_id = ""
        
        self.id_label.config(text=self.create_id())
        self.status_label.config(text="Idle")
        
        self.name_entry.config(state=tk.NORMAL)
        self.output_type_entry.config(state=tk.NORMAL)
        self.output_acodec_entry.config(state=tk.NORMAL)
        self.output_vcodec_entry.config(state=tk.NORMAL)
        
        self.start_button.config(state=tk.NORMAL)
        self.complete_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

        self.set_file_button.config(state=tk.NORMAL)
        self.set_folder_button.config(state=tk.NORMAL)
        self.set_interval_button.config(state=tk.NORMAL)

        self.progress_time_label.config(text="00:00:00")
        self.conversion_time_label.config(text="00:00:00")

        if self.is_copy_profile.get() == False:

            self.name_entry.delete(0, tk.END)

            self.input_path_label.config(text="Not Set")
            self.output_path_label.config(text="Not Set")

            self.input_vcodec_label.config(text="Unknown")
            self.input_acodec_label.config(text="Unknown")
            
            self.output_type_entry.delete(0, tk.END)
            self.output_type_entry.insert(0, "mp4")
            
            self.output_acodec_entry.delete(0, tk.END)
            self.output_acodec_entry.insert(0, "Unknown")

            self.output_vcodec_entry.delete(0, tk.END)
            self.output_vcodec_entry.insert(0, "Unknown")
            
            self.video_length_label.config(text="00:00:00")
            self.splice_interval_label.config(text="00:00:00 - 01:00:00")
            self.splice_length_label.config(text="01:00:00")

        self.is_copy_profile.set(False)

    def retain_profile(self):
        return

    def complete_edit(self):
        t = threading.Thread(target=self.complete_edit_thread)
        t.start()

    def complete_edit_thread(self):
        if self.current_process_id == "" or self.tasks[self.current_process_id] == "Success":
            messagebox.showwarning("Warning", "No process is running or already completed.")
            return
        
        #print("stopping")
        try:
            self.send_event(self.current_process_id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Stopping", self.queue_message)
            
            #self.terminate_process(self.tasks[self.current_process_id]["process"])
            self.tasks[self.current_process_id]["process"].communicate(input='q') # Send SIGTERM
            self.tasks[self.current_process_id]["process"].wait()  # Wait up to 5 seconds
            
            if self.tasks[self.current_process_id]["process"].poll() is None:
                self.tasks[self.current_process_id]["process"].kill()  # Force kill if still running
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during completion: {traceback.format_exc()}")

            with open("edit_complete_error.log", "a") as f:
                f.write(f"Error during compete process: {traceback.format_exc()}\n")

            #print("Error: " + traceback.format_exc())

            self.send_event(self.current_process_id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)

        finally:
            self.create_profile()
    
    def cancel_edit(self):
        t = threading.Thread(target=self.cancel_edit_thread)
        t.start()

    def cancel_edit_thread(self):
        if self.current_process_id == "" or self.tasks[self.current_process_id]["status"] == "Success":
            messagebox.showwarning("Warning", "No process is running or already Cancalled.")
            return
            
        try:
            self.send_event(self.current_process_id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Stopping", self.queue_message)
            # Stop the recording process
            self.tasks[self.current_process_id]["process"].communicate(input='q')
            self.tasks[self.current_process_id]["process"].wait()

            #self.terminate_process(self.tasks[self.current_process_id]["process"])

            # Remove the output file
            output_file = self.tasks[self.current_process_id]["output_file"]
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during cancellation: {traceback.format_exc()}")
            #print(f"Error during cancellation: {traceback.format_exc()}")
            # write a log in the current path
            with open("edit_cancel_error.log", "a") as f:
                f.write(f"Error during cancellation: {traceback.format_exc()}\n")

            self.send_event(self.current_process_id, "<<CheckEditQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
        finally:
            self.create_profile()
    
    def show_interval_window(self):
        self.interval_window_open = True
        interval_window = tk.Toplevel(self)
        interval_window.title("Set Splice Interval")
        interval_window.geometry("300x200")  # Increased height for duration display
        
        interval_window.transient(self)
        interval_window.grab_set()
        interval_window.focus_set()

        # Start time entry
        start_frame = tk.Frame(interval_window)
        start_frame.pack(pady=10)
        tk.Label(start_frame, text="Start Time (HH:MM:SS):").pack(side='left')
        start_entry = tk.Entry(start_frame, width=10)
        start_entry.insert(0, "00:00:00")
        start_entry.pack(side='left')
        
        # End time entry
        end_frame = tk.Frame(interval_window)
        end_frame.pack(pady=10)
        tk.Label(end_frame, text="End Time (HH:MM:SS):").pack(side='left')
        end_entry = tk.Entry(end_frame, width=10)
        end_entry.insert(0, "00:00:00")
        end_entry.pack(side='left')

        # Duration display
        duration_frame = tk.Frame(interval_window)
        duration_frame.pack(pady=10)
        duration_label = tk.Label(duration_frame, text="Duration: 00:00:00")
        duration_label.pack()
        
        def calculate_duration(*args):
            try:
                start_time = start_entry.get()
                end_time = end_entry.get()
                
                if re.match(r'^([0-9]{2}):([0-9]{2}):([0-9]{2})$', start_time) and re.match(r'^([0-9]{2}):([0-9]{2}):([0-9]{2})$', end_time):
                    start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
                    end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(":")))
                    
                    duration_seconds = end_seconds - start_seconds
                    if duration_seconds > 0:
                        hours = duration_seconds // 3600
                        minutes = (duration_seconds % 3600) // 60
                        seconds = duration_seconds % 60
                        duration_label.config(text=f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
            except ValueError:
                pass
        
        def validate_and_save():
            start_time = start_entry.get()
            end_time = end_entry.get()
            
            if not re.match(r'^([0-9]{2}):([0-9]{2}):([0-9]{2})$', start_time) or not re.match(r'^([0-9]{2}):([0-9]{2}):([0-9]{2})$', end_time):
                messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS")
                return
            
            if end_time <= start_time:
                messagebox.showerror("Error", "End time must be after start time.")
                return
            
            # Calculate total splice time
            start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
            end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(":")))
            total_seconds = end_seconds - start_seconds
            
            # Convert total seconds to HH:MM:SS format
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            total_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            self.splice_interval_label.config(text=f"{start_time} - {end_time}")
            self.splice_length_label.config(text=total_time)
            interval_window.destroy()

        # Bind entry changes to duration calculation
        start_entry.bind('<KeyRelease>', calculate_duration)
        end_entry.bind('<KeyRelease>', calculate_duration)
        
        tk.Button(interval_window, text="Save", command=validate_and_save).pack(pady=20)

    def check_duplicate_filename(self, output_file):
        if os.path.exists(output_file):
            response = messagebox.askyesno(
                "File Exists", 
                "A file with this name already exists. Do you want to overwrite it?"
            )
            
            if not response:
                return False
            else:
                os.remove(output_file)
                return True
        return True