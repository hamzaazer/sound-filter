import customtkinter as ctk
import numpy as np
import soundfile as sf
import os
import time
import threading
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TimingDialog(ctk.CTkToplevel):
    def __init__(self, *args, timings=None, sort_method=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Function Timings")
        self.geometry("400x300")

        title_label = ctk.CTkLabel(self, 
                                   text="Function Timings", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)

        timing_frame = ctk.CTkFrame(self)
        timing_frame.pack(padx=20, pady=10, fill="x", expand=True)

        timing_labels = [
            
            "merge_sort", 
            "quicke Sort",
            "insert sort"
        ]

        for i, (label, timing) in enumerate(zip(timing_labels, timings)):
            func_label = ctk.CTkLabel(timing_frame, 
                                      text=f"{label}:", 
                                      anchor="w")
            func_label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            time_label = ctk.CTkLabel(timing_frame, 
                                      text=f"{timing:.4f} seconds", 
                                      text_color="lightblue")
            time_label.grid(row=i, column=1, sticky="w", padx=5, pady=5)

        close_button = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_button.pack(pady=20)

class SoundAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sound File Analyzer")
        self.geometry("900x700")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.main_frame, 
                                        text="Sound File Analyzer", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        self.folder_selection_frame = ctk.CTkFrame(self.main_frame)
        self.folder_selection_frame.pack(fill="x", pady=10)

        self.folder_label = ctk.CTkLabel(self.folder_selection_frame, text="Select Sound Folder:")
        self.folder_label.pack(side="left", padx=10)

        self.folder_path = ctk.StringVar()
        self.folder_entry = ctk.CTkEntry(self.folder_selection_frame, 
                                         textvariable=self.folder_path, 
                                         width=500)
        self.folder_entry.pack(side="left", padx=10, expand=True, fill="x")

        self.browse_button = ctk.CTkButton(self.folder_selection_frame, 
                                           text="Browse", 
                                           command=self.browse_folder)
        self.browse_button.pack(side="right", padx=10)

        self.sort_method = ctk.StringVar(value="duration")
        self.sort_label = ctk.CTkLabel(self.main_frame, text="Select Sort Key:")
        self.sort_label.pack(pady=10)

        self.sort_frame = ctk.CTkFrame(self.main_frame)
        self.sort_frame.pack(pady=10)

        sort_keys = [
            ("Duration", "duration"),
            ("Volume", "volume"),
            ("Sample Rate", "sample_rate")
        ]



        self.sort_key = ctk.StringVar(value="duration")
        for text, value in sort_keys:
            radio = ctk.CTkRadioButton(self.sort_frame, 
                                       text=text, 
                                       variable=self.sort_key, 
                                       value=value)
            radio.pack(side="left", padx=10)

 
 

        self.analyze_button = ctk.CTkButton(self.main_frame, 
                                            text="Analyze Sound Files", 
                                            command=self.start_analysis)
        self.analyze_button.pack(pady=20)

        self.results_textbox = ctk.CTkTextbox(self.main_frame, 
                                              width=800, 
                                              height=300)
        self.results_textbox.pack(padx=20, pady=20, expand=True, fill="both")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        self.folder_path.set(folder)

    def start_analysis(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return

        self.results_textbox.delete("1.0", "end")
        threading.Thread(target=self.analyze_sounds, daemon=True).start()

    def analyze_sounds(self):
        start_total_time = time.time()
        folder = self.folder_path.get()
        sort_key = self.sort_key.get()
        sort_method = self.sort_method.get()

        timings = [0, 0, 0]

        
        sound_files = self.import_sound_files(folder)
        
        if not sound_files:
            self.update_results("No sound files found.")
            return

        start_time = time.time()
        sound_properties = self.analyze_sound_files(sound_files)
        
        start_time1 = time.time()
        sorted_results = self.merge_sort(sound_properties, sort_key)
        timings[0] = time.time() - start_time1
        start_time = time.time()

        sorted_results = self.quick_sort(sound_properties, sort_key)
        
        timings[1] = time.time() - start_time

        start_time2 = time.time()
        sorted_results = self.insert_sort(sound_properties, sort_key)
        timings[2] = time.time() - start_time2

        

        self.after(0, self.display_results, sorted_results, timings, sort_method)

    def import_sound_files(self, directory, extensions=['.wav', '.mp3', '.flac']):
        sound_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    sound_files.append(os.path.join (root, file))
        return sound_files

    def analyze_sound_files(self, files):
        sound_properties = []
        for file in files:
            try:
                data, sample_rate = sf.read(file)
                duration = len(data) / sample_rate
                volume = np.max(np.abs(data))
                
                sound_properties.append({
                    'filename': file,
                    'duration': duration,
                    'volume': volume,
                    'sample_rate': sample_rate
                })
            except Exception as e:
                print(f"Error analyzing {file}: {e}")
        return sound_properties

    def merge_sort(self, arr, key):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid], key)
        right = self.merge_sort(arr[mid:], key)
        
        return self.merge(left, right, key)

    def merge(self, left, right, key):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i][key] <= right[j][key]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result

    def quick_sort(self, arr, key):
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2][key]
        left = [x for x in arr if x[key] < pivot]
        middle = [x for x in arr if x[key] == pivot]
        right = [x for x in arr if x[key] > pivot]
        
        return self.quick_sort(left, key) + middle + self.quick_sort(right, key)

    def insert_sort(self, arr, key):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j][key] > arr[j + 1][key]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    def display_results(self, sorted_results, timings, sort_method):
        self.results_textbox.delete("1.0", "end")
        
        for sound in sorted_results:
            self.results_textbox.insert("end", f"File: {os.path.basename(sound['filename'])}\n"
                f"Duration: {sound['duration']:.2f} seconds\n"
                f"Volume: {sound['volume']:.2f}\n"
                f"Sample Rate: {sound['sample_rate']}\n\n"
            )
        
        TimingDialog(self, timings=timings, sort_method=sort_method)

if __name__ == "__main__":
    app = SoundAnalyzerApp()
    app.mainloop()