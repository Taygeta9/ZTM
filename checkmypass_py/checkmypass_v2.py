import requests
import hashlib
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import aiohttp
import asyncio

class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Leak Checker")
        self.root.configure(bg='#1E1E1E')
        self.root.resizable(False, False)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', background='#FF9500', foreground='white',
                       font=('Helvetica', 10, 'bold'), borderwidth=0)
        style.map('TButton', background=[('active', '#FF6B00')])
        style.configure('TLabel', background='#1E1E1E', foreground='#FF9500',
                       font=('Helvetica', 11))
        style.configure('TCheckbutton', background='#1E1E1E', foreground='#FF9500')
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input
        self.label = ttk.Label(self.main_frame, text="Enter Password:")
        self.label.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.password_entry = tk.Entry(self.main_frame, width=30, bg='#2D2D2D',
                                     fg='white', insertbackground='white',
                                     relief='flat', show='•')
        self.password_entry.grid(row=1, column=0, pady=5, padx=5)
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        self.show_password_check = ttk.Checkbutton(self.main_frame, text="Show Password",
                                                 variable=self.show_password_var,
                                                 command=self.toggle_password_visibility)
        self.show_password_check.grid(row=1, column=1, pady=5, padx=5)
        
        # Buttons
        self.check_button = ttk.Button(self.main_frame, text="Check Password",
                                     command=self.check_password)
        self.check_button.grid(row=2, column=0, pady=10)
        
        self.clear_button = ttk.Button(self.main_frame, text="Clear",
                                     command=self.clear_input)
        self.clear_button.grid(row=2, column=1, pady=10, padx=5)
        
        # Results
        self.results_text = scrolledtext.ScrolledText(self.main_frame, width=40,
                                                    height=10, bg='#2D2D2D',
                                                    fg='white', font=('Helvetica', 10),
                                                    wrap=tk.WORD, relief='flat')
        self.results_text.grid(row=3, column=0, pady=5, padx=5, columnspan=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                                  background='#1E1E1E', foreground='#FF9500')
        self.status_bar.grid(row=4, column=0, pady=5, columnspan=2, sticky=tk.W+tk.E)
        
        # History
        self.history = []
        self.show_history_var = tk.BooleanVar()
        self.history_check = ttk.Checkbutton(self.main_frame, text="Show History",
                                           variable=self.show_history_var,
                                           command=self.toggle_history)
        self.history_check.grid(row=5, column=0, pady=5, columnspan=2)
        
        # Bindings
        self.root.bind('<Return>', lambda e: self.check_password())
        self.root.bind('<Escape>', lambda e: self.clear_input())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window
        self.root.update()
        self.root.geometry(f"450x400+{int(self.root.winfo_screenwidth()/2-225)}+{int(self.root.winfo_screenheight()/2-200)}")

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='•')

    async def request_api_data(self, query_char):
        url = 'https://api.pwnedpasswords.com/range/' + query_char
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
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
            self.results_text.insert(tk.END, "History hidden")

    def clear_input(self):
        self.password_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def check_password(self):
        password = self.password_entry.get().strip()
        if not password:
            self.show_message("Error", "Please enter a password!", "red")
            return
        if len(password) < 4:
            self.show_message("Warning", "Password seems too short to be secure!", "orange")
            return
            
        self.status_var.set("Checking...")
        try:
            loop = asyncio.get_event_loop()
            count = loop.run_until_complete(self.pwned_api_check(password))
            self.results_text.delete(1.0, tk.END)
            strength = self.get_password_strength(password)
            if count:
                result = f"'{password}' was found {count} times!\nYou should change your password immediately!\nPassword strength: {strength}/5"
            else:
                result = f"'{password}' was NOT found in any leaks.\nLooks good!\nPassword strength: {strength}/5"
            self.results_text.insert(tk.END, result)
            self.history.append(result)
            self.status_var.set("Check complete!")
        except Exception as e:
            self.show_message("Error", str(e), "red")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()