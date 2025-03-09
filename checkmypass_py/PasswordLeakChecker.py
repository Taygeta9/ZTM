import requests
import hashlib
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import aiohttp
import asyncio
from datetime import datetime

class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Leak Checker")
        self.is_dark_mode = True
        self.set_theme('#1E1E1E', '#FF9500', '#2D2D2D', 'white')
        self.root.resizable(False, False)
        
        # Style configuration
        self.style = ttk.Style()
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input
        self.label = ttk.Label(self.main_frame, text="ENTER PASSWORD", anchor='center')
        self.label.grid(row=0, column=0, pady=(0, 10), padx=5)  # Removed sticky=tk.W for center alignment
        
        self.password_entry = tk.Entry(self.main_frame, width=40,
                                     bg=self.entry_bg, fg=self.text_fg,
                                     insertbackground=self.text_fg,
                                     font=('Orbitron', 10, 'bold'),
                                     borderwidth=0, relief='flat',
                                     show='•')
        self.password_entry.grid(row=1, column=0, pady=5, padx=5)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.grid(row=2, column=0, pady=10, sticky=tk.EW)
        
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_check = ttk.Checkbutton(self.controls_frame, text="SHOW",
                                                 variable=self.show_password_var,
                                                 command=self.toggle_password_visibility)
        self.show_password_check.grid(row=0, column=0, padx=5)
        
        self.theme_var = tk.BooleanVar(value=True)
        self.theme_check = ttk.Checkbutton(self.controls_frame, text="DARK",
                                         variable=self.theme_var,
                                         command=self.toggle_theme)
        self.theme_check.grid(row=0, column=1, padx=5)
        
        self.check_button = ttk.Button(self.controls_frame, text="CHECK",
                                     command=self.check_password)
        self.check_button.grid(row=0, column=2, padx=5)
        
        self.clear_button = ttk.Button(self.controls_frame, text="CLEAR",
                                     command=self.clear_input)
        self.clear_button.grid(row=0, column=3, padx=5)
        
        self.export_button = ttk.Button(self.controls_frame, text="EXPORT",
                                      command=self.export_history)
        self.export_button.grid(row=0, column=4, padx=5)
        
        # Strength meter
        self.strength_label = ttk.Label(self.main_frame, text="STRENGTH", anchor='center')
        self.strength_label.grid(row=3, column=0, pady=(10, 5), padx=5)  # Removed sticky=tk.W for center alignment
        self.strength_meter = ttk.Progressbar(self.main_frame, length=300,
                                            maximum=5, mode='determinate')
        self.strength_meter.grid(row=4, column=0, pady=5, padx=5, sticky=tk.EW)
        
        # Results
        self.results_text = scrolledtext.ScrolledText(self.main_frame, width=50,
                                                    height=10, bg=self.entry_bg,
                                                    fg=self.text_fg, font=('Orbitron', 9, 'bold'),
                                                    wrap=tk.WORD, borderwidth=0, relief='flat')
        self.results_text.grid(row=5, column=0, pady=10, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=6, column=0, pady=5, sticky=tk.EW)
        
        # History
        self.history = []
        self.show_history_var = tk.BooleanVar()
        self.history_check = ttk.Checkbutton(self.main_frame, text="HISTORY",
                                           variable=self.show_history_var,
                                           command=self.toggle_history)
        self.history_check.grid(row=7, column=0, pady=5)
        
        # Apply styles
        self.update_styles()
        
        # Bindings
        self.root.bind('<Return>', lambda e: self.check_password())
        self.root.bind('<Escape>', lambda e: self.clear_input())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Window geometry
        self.root.geometry(f"600x500+{int(self.root.winfo_screenwidth()/2-300)}+{int(self.root.winfo_screenheight()/2-250)}")
        
        # Asyncio setup
        self.loop = asyncio.get_event_loop()

    def set_theme(self, bg, accent, entry_bg, text_fg):
        self.bg = bg
        self.accent = accent
        self.entry_bg = entry_bg
        self.text_fg = text_fg
        self.root.configure(bg=bg)

    def update_styles(self):
        self.style.theme_use('clam')
        self.style.configure('TButton', background=self.accent, foreground=self.text_fg,
                           font=('Orbitron', 10, 'bold'), borderwidth=0, padding=5)
        self.style.map('TButton', background=[('active', '#FF6B00' if self.is_dark_mode else '#8A2BE2')])
        self.style.configure('TLabel', background=self.bg, foreground=self.accent,
                           font=('Orbitron', 10, 'bold'))
        self.style.configure('TCheckbutton', background=self.bg, foreground=self.accent,
                           font=('Orbitron', 10, 'bold'))
        self.style.configure('Horizontal.TProgressbar', background=self.accent,
                           troughcolor=self.entry_bg)
        self.status_bar.configure(background=self.bg, foreground=self.accent,
                                font=('Orbitron', 9, 'bold'))
        self.password_entry.configure(bg=self.entry_bg, fg=self.text_fg,
                                    insertbackground=self.text_fg)
        self.results_text.configure(bg=self.entry_bg, fg=self.text_fg)

    def toggle_theme(self):
        self.is_dark_mode = self.theme_var.get()
        if self.is_dark_mode:
            self.set_theme('#1E1E1E', '#FF9500', '#2D2D2D', 'white')
        else:
            self.set_theme('#FFFFFF', '#9932CC', '#F0F0F0', 'black')
        self.update_styles()

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='•')

    async def request_api_data(self, query_char):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.pwnedpasswords.com/range/{query_char}') as res:
                if res.status != 200:
                    raise RuntimeError(f'Error fetching: {res.status}')
                return await res.text()

    def get_password_leaks_count(self, hashes, hash_to_check):
        hashes = (line.split(':') for line in hashes.splitlines())
        for h, count in hashes:
            if h == hash_to_check:
                return count
        return 0

    def get_password_strength(self, password):
        score = 0
        if len(password) > 8: score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*" for c in password): score += 1
        return score

    async def pwned_api_check(self, password):
        sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        first5_char, tail = sha1password[:5], sha1password[5:]
        response = await self.request_api_data(first5_char)
        return self.get_password_leaks_count(response, tail)

    def show_message(self, prefix, message, color):
        self.status_var.set(f"{prefix}: {message}")
        self.status_bar.configure(foreground=color)
        self.root.after(5000, lambda: self.status_var.set(""))

    def toggle_history(self):
        self.results_text.delete(1.0, tk.END)
        if self.show_history_var.get():
            self.results_text.insert(tk.END, "\n\n".join(self.history))
        else:
            self.results_text.insert(tk.END, "HISTORY CLEARED")

    def clear_input(self):
        self.password_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("")
        self.strength_meter['value'] = 0

    def export_history(self):
        if not self.history:
            self.show_message("INFO", "NO HISTORY TO EXPORT", "orange")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                              filetypes=[("Text files", "*.txt")],
                                              initialfile=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if filename:
            with open(filename, 'w') as f:
                f.write("\n\n".join(self.history))
            self.show_message("SUCCESS", "HISTORY EXPORTED", "green")

    def on_closing(self):
        if messagebox.askokcancel("EXIT", "TERMINATE PROCESS?"):
            self.root.destroy()

    def check_password(self):
        password = self.password_entry.get().strip()
        if not password:
            self.show_message("ERROR", "NO INPUT DETECTED", "red")
            return
            
        self.status_var.set("PROCESSING...")
        self.results_text.delete(1.0, tk.END)
        
        async def check_single():
            if len(password) < 4:
                self.root.after(0, lambda: self.show_message("WARNING", f"'{password}' TOO WEAK", "orange"))
                return
                
            try:
                count = await self.pwned_api_check(password)
                strength = self.get_password_strength(password)
                
                self.root.after(0, lambda s=strength: self.strength_meter.configure(value=s))
                display_pass = password if self.show_password_var.get() else '[SECURED]'
                result = f"PASSWORD: {display_pass}\n"
                if count:
                    result += f"LEAKED {count} TIMES - UPDATE REQUIRED\n"
                else:
                    result += "NO LEAKS DETECTED\n"
                result += f"STRENGTH: {strength}/5"
                
                self.root.after(0, lambda r=result: self.results_text.insert(tk.END, r + "\n"))
                self.history.append(result)
            except Exception as e:
                self.root.after(0, lambda e=e: self.show_message("ERROR", str(e), "red"))
            
            self.root.after(0, lambda: self.status_var.set("PROCESS COMPLETE"))

        self.loop.create_task(check_single())

def main():
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    while True:
        try:
            root.update()
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
        except tk.TclError:
            break
    root.mainloop()

if __name__ == '__main__':
    main()