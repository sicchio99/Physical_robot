import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import requests
from Project_start.read_Config import ReadConfig


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Controllo di Start e Stop")
        self.master.geometry("850x600")
        self.master.resizable(False, False)

        # Load and resize the image with antialiasing
        image = Image.open("kobuki.jpg")
        image = image.resize((600, 400), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
        photo = ImageTk.PhotoImage(image)
        self.label = tk.Label(master, image=photo)
        self.label.image = photo  # Avoid garbage collection
        self.label.pack(pady=20)

        # Buttons
        self.stop_button = tk.Button(master, text="Stop", command=self.stop, font=("Helvetica", 20), bg="#f44336",
                                     fg="white", padx=30, pady=15, state=tk.NORMAL)
        self.stop_button.pack(side=tk.BOTTOM, pady=20)

        self.start_button = tk.Button(master, text="Start", command=self.start, font=("Helvetica", 20), bg="#4CAF50",
                                      fg="white", padx=30, pady=15)
        self.start_button.pack(side=tk.BOTTOM)

    def start(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        messagebox.showinfo("Message", "Simulation will start shortly!")
        # subprocess.Popen(["bash", "start.sh"])
        config = ReadConfig()
        ip = config.read_data("IP_RASPBERRY")
        r = requests.get(f'http://{ip}:5008/start')

    def stop(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        messagebox.showinfo("Message", "Simulation has been stopped!")
        # subprocess.Popen(["bash", "stop.sh"])
        config = ReadConfig()
        ip = config.read_data("IP_RASPBERRY")
        r = requests.get(f'http://{ip}:5008/stop')


if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
