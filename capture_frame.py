import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import os
import queue
import requests
import time
import traceback
import re

from Media_Info import MediaInfo
from Ticket import Ticket,TicketPurpose

class CaptureFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_copy_profile = tk.BooleanVar()
        self.setup_main_panel()
        self.setup_data_table()
        self.tasks = {}
        self.current_process_id = ""
        self.bind("<<CheckCaptureQueue>>", self.check_queue)
        self.queue_message = queue.Queue()
        self.bind("<<UpdateCaptureTime>>", self.update_progress)
        self.time_queue = queue.Queue()

    def update_progress(self,event):
        msg: Ticket
        msg = self.time_queue.get()

        #print(f"Processing event at {time.time()} type: {msg.ticket_type}")
        if msg.ticket_type == TicketPurpose.UI_TABLE_PROGRESS:
            self.update_data_table_time(msg.ticket_id, msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_FORM_PROGRESS:
            self.capturing_time_label.config(text=msg.ticket_value)
        else:
            if msg.ticket_id == "" or msg.ticket_id not in self.tasks:
                return
            
            self.tasks[msg.ticket_id][msg.ticket_type.value] = msg.ticket_value

    def check_queue(self, event):
        msg: Ticket
        msg = self.queue_message.get()
        
        if msg.ticket_type == TicketPurpose.UI_TABLE_STATUS:
            self.update_data_table_status(msg.ticket_id, msg.ticket_value)
        elif msg.ticket_type == TicketPurpose.UI_TABLE_NEW_TABLE:
            self.update_data_table(msg.ticket_value['id'], msg.ticket_value['name'], msg.ticket_value['url'], msg.ticket_value['video_type'], msg.ticket_value['status'], msg.ticket_value['capturing_time'])
        else:
            if msg.ticket_id == "" or msg.ticket_id not in self.tasks:
                return
            
            self.tasks[msg.ticket_id][msg.ticket_type.value] = msg.ticket_value

    # Move all capture-related methods here
    def setup_main_panel(self):
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(frame, text="Id:").grid(row=0, column=0, sticky='w')
        self.id_label = tk.Label(frame, text="1")
        self.id_label.grid(row=0, column=1, sticky='w')
        
        tk.Label(frame, text="Video Source URL:").grid(row=1, column=0, sticky='w')
        self.url_entry = tk.Entry(frame, width=50)
        self.url_entry.grid(row=1, column=1, sticky='w')

        tk.Label(frame, text="Video Output Name:").grid(row=2, column=0, sticky='w')
        self.name_entry = tk.Entry(frame, width=50)
        self.name_entry.grid(row=2, column=1)

        tk.Label(frame, text="Output Path:").grid(row=3, column=0, sticky='w')
        self.output_path_label = tk.Label(frame, text="Not Set")
        self.output_path_label.grid(row=3, column=1, sticky='w')
        self.set_folder_button = tk.Button(frame, text="Set Folder", command=self.set_output_folder)
        self.set_folder_button.grid(row=3, column=2)

        tk.Label(frame, text="Output Type:").grid(row=4, column=0, sticky='w')
        self.output_type_entry = tk.Entry(frame, width=50)
        self.output_type_entry.insert(0, "mp4")
        self.output_type_entry.grid(row=4, column=1)

        tk.Label(frame, text="Capturing Time:").grid(row=5, column=0, sticky='w')
        self.capturing_time_label = tk.Label(frame, text="00:00:00")
        self.capturing_time_label.grid(row=5, column=1, sticky='w')

        tk.Label(frame, text="Type:").grid(row=6, column=0, sticky='w')
        self.type_label = tk.Label(frame, text="Unknown")
        self.type_label.grid(row=6, column=1, sticky='w')

        tk.Label(frame, text="Status:").grid(row=7, column=0, sticky='w')
        self.status_label = tk.Label(frame, text="Idle")
        self.status_label.grid(row=7, column=1, sticky='w')

        self.isCopy_checkbox = tk.Checkbutton(frame, text="copy the current profile while creating new profile", variable=self.is_copy_profile, command=self.retain_profile).grid(row=8, column=0, columnspan=2, sticky='w')

        task_button_group = tk.Frame(frame)
        task_button_group.grid(row=9, column=0, columnspan=3, sticky='ew')

        tk.Button(task_button_group, text="Create profile", command=self.create_profile).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.start_button = tk.Button(task_button_group, text="Start Capture", command=self.start_capture)
        self.start_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.complete_button = tk.Button(task_button_group, text="Complete", state=tk.DISABLED, command=self.complete_capture)
        self.complete_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.cancel_button = tk.Button(task_button_group, text="Cancel", state=tk.DISABLED, command=self.cancel_capture)
        self.cancel_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    def set_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path_label.config(text=folder)

    def start_capture(self):
        threading.Thread(target=self.set_capture_thread).start()

    def set_capture_thread(self):
        self.current_process_id = None
        url = self.url_entry.get()
        output_name = self.name_entry.get()
        output_path = self.output_path_label.cget("text")
        output_type = self.output_type_entry.get()
        status = "Capturing"
        id = self.create_id()

        if not all([url, output_name, output_path, output_type]):
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return
        
        #if not self.check_url(url):
        #    return
        
        info = MediaInfo(url)
        if info.check_file():
            metadata = info.get_json()
            video_type = metadata["type"]

        output_file = os.path.join(output_path, f"{output_name}.{output_type}")

        if not self.check_duplicate_filename(output_file):
            return

        # Update the status and data table
        self.status_label.config(text=status)

        self.tasks[id] = {"id":id, 
                           "name": output_name, 
                           "url":url, 
                           "video_type": video_type, 
                           "status":status, 
                           "capturing_time":"00:00:00",
                           "output_path":output_path,
                           "output_type":output_type,
                           "output_file": output_file,
                           "process":None}

        #self.update_data_table(id, output_name, url, video_type, status, "00:00:00")
        self.send_event("", "<<CheckCaptureQueue>>",TicketPurpose.UI_TABLE_NEW_TABLE, self.tasks[id], self.queue_message)
        threading.Thread(target=self.capture_video, args=(id, url, output_file)).start()

        self.create_profile()

    def setup_data_table(self):
        # Create data table frame
        self.table_frame = tk.Frame(self)
        self.table_frame.grid(column=0, row=2, sticky='w')
        
        self.tree = ttk.Treeview(self.table_frame, columns=("name", "url", "type", "status", "time"), show='headings')
        self.tree.heading("name", text="Name")
        self.tree.heading("url", text="URL")
        self.tree.heading("type", text="Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("time", text="Capturing Time")
        self.tree.grid(column=0, row=0, pady=10, padx=10)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)


    def on_row_click(self, event):
        if len(self.tree.selection()) == 0:
            return

        self.start_button.config(state=tk.DISABLED)

        self.current_process_id = str(self.tree.selection()[0])
        task = self.tasks[self.current_process_id]
        self.id_label.config(text=self.current_process_id)

        self.set_folder_button.config(state=tk.DISABLED)

        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, task["url"])
        self.url_entry.config(state=tk.DISABLED)
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, task["name"])
        self.name_entry.config(state=tk.DISABLED)

        self.output_path_label.config(text=task["output_path"])
        self.output_type_entry.delete(0, tk.END)
        self.output_type_entry.insert(0, task["output_type"])
        self.output_type_entry.config(state=tk.DISABLED)
        
        self.type_label.config(text=task["video_type"])
        self.status_label.config(text=task["status"])
        self.capturing_time_label.config(text=task["capturing_time"])
        
        self.complete_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def send_event(self, id, event_name, event_type, event_data, queue):
        ticket = Ticket(id, event_type, event_data)
        queue.put(ticket)
        self.event_generate(event_name)

    def capture_video(self,id, url, output_file):
        #print(f"Capturing video from {url} to {output_file}")
        command = f'ffmpeg -hide_banner -i "{url}" -c copy {output_file}'

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
            
        #t = threading.Thread(target=process_output, 
        #        args=(self.tasks[id]["process"].stderr, output_queue))
        t = threading.Thread(target=process_output)
        t.daemon = True
        t.start()

        time_pattern = r"frame=.*time=\s*([0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{2})"
        while True:
            try:
                line = output_queue.get_nowait()

                #print(f"Capturing time: {line}")
                time_match = re.search(time_pattern, line)
                if time_match:
                    elapsed_time = line.split("time=")[1].split(" ")[0]
                    self.send_event(id, "<<UpdateCaptureTime>>", TicketPurpose.UI_TABLE_PROGRESS, elapsed_time, self.time_queue)
                    self.send_event(id, "<<UpdateCaptureTime>>", TicketPurpose.CAPTURING_TIME, elapsed_time, self.time_queue)

                    if self.current_process_id == id:
                        self.send_event(id, "<<UpdateCaptureTime>>", TicketPurpose.UI_FORM_PROGRESS, elapsed_time, self.time_queue)

            except queue.Empty:
                # Check if process is still running
                #if self.tasks[id]["process"].poll() is not None:
                #    print(f"returncode: {self.tasks[id]['process'].returncode}")
                #    break
                #continue
                if self.tasks[id]["process"].poll() is not None:
                    if self.tasks[id]["process"].returncode == 0:
                        self.send_event(id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Success", self.queue_message)
                        return
                    else:
                        self.send_event(id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
                    break
                pass
            except Exception as e:
                print(f"Error: {traceback.format_exc()}")
                break
                
        #self.send_event(id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Success", self.queue_message)
            
    def update_data_table(self, id, name, url, video_type, status, time ):
        self.tree.insert('', 'end', id=id, values=(name, url, video_type, status, time))

    def update_data_table_time(self, id, time):
        self.tree.item(id, values=(self.tasks[id]["name"], self.tasks[id]["url"], self.tasks[id]["video_type"], self.tasks[id]["status"], time))
        self.tree.update()

    def update_data_table_status(self, id, status):
        self.tasks[id]["status"] = status
        self.tree.item(id, values=(self.tasks[id]["name"], self.tasks[id]["url"], self.tasks[id]["video_type"], status, self.tasks[id]["capturing_time"]))
        self.tree.update()

    def create_id(self):
        return "1" if len(self.tasks) == 0 else str(int(max(self.tasks))+1)
    
    def create_profile(self):
        self.current_process_id = ""
        self.start_button.config(state=tk.NORMAL)
        self.capturing_time_label.config(text="00:00:00")
        self.status_label.config(text="Idle")
        self.id_label.config(text=self.create_id())
        
        self.url_entry.config(state=tk.NORMAL)
        self.name_entry.config(state=tk.NORMAL)
        self.output_type_entry.config(state=tk.NORMAL)
    
        self.complete_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

        self.set_folder_button.config(state=tk.NORMAL)
        if self.is_copy_profile.get() == False:
            self.clear_profile()

        self.is_copy_profile.set(False)

    def retain_profile(self):
        return

    def clear_profile(self):
        # rest all the entry and the second label in the same row
        self.id_label.config(text=self.create_id())
        self.url_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.output_type_entry.delete(0, tk.END)
        self.output_path_label.config(text="Not Set")
        self.status_label.config(text="Idle")
        self.type_label.config(text="Unknown")
        self.capturing_time_label.config(text="00:00:00")
        self.start_button.config(state=tk.NORMAL)
        self.set_folder_button.config(state=tk.NORMAL)
        self.complete_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.current_process_id = ""
        return
    
    def cancel_capture(self):
        t = threading.Thread(target=self.cancel_capture_thread)
        t.start()

    def cancel_capture_thread(self):
        if self.current_process_id == "" or self.tasks[self.current_process_id]["status"] == "Success":
            messagebox.showwarning("No Active Capture", "No active capture to cancel.")
            return
        
        self.send_event(self.current_process_id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Stopping", self.queue_message)
        try:
            # Stop the recording process
            self.tasks[self.current_process_id]["process"].communicate(input='q')
            self.tasks[self.current_process_id]["process"].wait()

            # Remove the output file
            output_file = self.tasks[self.current_process_id]["output_file"]
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during cancellation: {traceback.format_exc()}")
            print(f"Error during cancellation: {traceback.format_exc()}")
            # write a log in the current path
            with open("capture_cancel_error.log", "a") as f:
                f.write(f"Error during cancellation: {traceback.format_exc()}\n")
            
            self.send_event(self.current_process_id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
        finally:
            self.create_profile()
            
    def complete_capture(self):
        t = threading.Thread(target=self.complete_capture_thread)
        t.start()

    def complete_capture_thread(self):
        if self.current_process_id == "" or self.tasks[self.current_process_id] == "Success":
            messagebox.showwarning("No Active Capture", "No active capture to complete.")
            return
        
        #print("stopping")
        self.send_event(self.current_process_id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Stopping", self.queue_message)
        try:
            #self.terminate_process(self.tasks[self.current_process_id]["process"])
            self.tasks[self.current_process_id]["process"].communicate(input='q') # Send SIGTERM
            self.tasks[self.current_process_id]["process"].wait()  # Wait up to 5 seconds
            
            if self.tasks[self.current_process_id]["process"].poll() is None:
                self.tasks[self.current_process_id]["process"].kill()  # Force kill if still running
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during completion: {traceback.format_exc()}")
            print(f"Error during complete the job: {traceback.format_exc()}")

            with open("capture_complete_error.log", "a") as f:
                f.write(f"Error during cancellation: {traceback.format_exc()}\n")
            
            self.send_event(self.current_process_id, "<<CheckCaptureQueue>>", TicketPurpose.UI_TABLE_STATUS, "Failed", self.queue_message)
        finally:
            self.create_profile()

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