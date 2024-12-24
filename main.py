import os
import threading
import tkinter as tk
from tkinter import ttk

from yt_dlp import YoutubeDL

# Global flag to track cancellation
cancel_flag = False

username = os.environ.get("USERNAME")


# Function to download video or audio
def download_video():
    global cancel_flag
    cancel_flag = False  # Reset the cancel flag
    url = url_entry.get()
    format_choice = format_var.get()  # Get the selected format

    if not url.strip():
        status_label.config(text="Please enter a valid URL.", fg="red")
        return

    # Disable buttons during download
    download_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)
    status_label.config(text="Fetching video details...", fg="blue")

    def run_download():
        try:
            # Ensure the "Videos" folder exists
            output_folder = f"C:\\Users\\{username}\\Videos"
            os.makedirs(output_folder, exist_ok=True)

            # Fetch video details
            ydl_opts_info = {"quiet": True}
            with YoutubeDL(ydl_opts_info) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get("title", "Unknown Title")

            # Update the status label with the video title
            status_label.config(text=f"Downloading: {video_title}", fg="blue")

            # Configure yt_dlp options for downloading
            ydl_opts = {
                "progress_hooks": [progress_hook],
                "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
            }

            if format_choice == "MP3":
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    },
                ]
            elif format_choice == "MP4":
                ydl_opts["format"] = "bestvideo+bestaudio/best"

            # Start downloading
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if not cancel_flag:
                status_label.config(
                    text=f"Download completed: {video_title}", fg="green"
                )
        except Exception as e:
            if cancel_flag:
                status_label.config(text="Download canceled.", fg="orange")
            else:
                status_label.config(text=f"Error: {str(e)}", fg="red")
        finally:
            # Enable buttons after download
            download_button.config(state=tk.NORMAL)
            cancel_button.config(state=tk.DISABLED)
            progress_bar["value"] = 0

    threading.Thread(target=run_download).start()


# Function to cancel download
def cancel_download():
    global cancel_flag
    cancel_flag = True  # Set the cancel flag to True
    status_label.config(text="Cancelling download...", fg="orange")


# Progress hook for yt_dlp
def progress_hook(d):
    global cancel_flag
    if cancel_flag:
        raise Exception("Download cancelled by user.")
    if d["status"] == "downloading":
        total_bytes = d.get("total_bytes", 0)
        downloaded_bytes = d.get("downloaded_bytes", 0)
        if total_bytes > 0:
            percentage = (downloaded_bytes / total_bytes) * 100
            progress_bar["value"] = percentage
        status_label.config(text=f"Downloading... {int(progress_bar['value'])}%")


# Create the main window
root = tk.Tk()
root.title("Useless Video Downloader by Shajin")
root.geometry("1080x480")

# Add a label
label = tk.Label(root, text="Enter YouTube Video URL:", font=("Arial", 18))
label.pack(pady=10)

# Add an entry box for the URL
url_entry = tk.Entry(root, width=60, font=("Arial", 20))
url_entry.pack(pady=5)

# Add a dropdown menu for format selection
format_var = tk.StringVar(value="MP4")  # Default value
format_label = tk.Label(root, text="Select Format:", font=("Arial", 18))
format_label.pack(pady=5)

format_dropdown = ttk.Combobox(
    root,
    textvariable=format_var,
    values=["MP4", "MP3"],
    state="readonly",
    font=("Arial", 16),
)
format_dropdown.pack(pady=5)

# Add a progress bar
progress_bar = ttk.Progressbar(
    root,
    orient="horizontal",
    length=400,
    mode="determinate",
)
progress_bar.pack(pady=10)

# Add a status label
status_label = tk.Label(root, text="", font=("Arial", 18))
status_label.pack(pady=5)

# Add buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

download_button = tk.Button(
    button_frame, text="Download", command=download_video, font=("Arial", 14)
)
download_button.grid(row=0, column=0, padx=10)

cancel_button = tk.Button(
    button_frame,
    text="Cancel",
    command=cancel_download,
    state=tk.DISABLED,
    font=("Arial", 14),
)
cancel_button.grid(row=0, column=1, padx=10)

# Run the application
# root.iconbitmap("icon.ico")
root.mainloop()
