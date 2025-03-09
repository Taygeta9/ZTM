import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import webbrowser
from tkinter import Menu

class HackerNewsScraper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hacker News Scraper")
        self.window.geometry("800x600")
        
        # Color schemes
        self.dark_mode = True
        self.dark_bg = "#2b2b2b"
        self.dark_fg = "#ffffff"
        self.dark_accent = "#4a4a4a"
        self.light_bg = "#ffffff"
        self.light_fg = "#000000"
        self.light_accent = "#e0e0e0"
        self.dark_link_color = "#ffff00"  # Yellow for dark mode
        self.light_link_color = "#800080"  # Purple for light mode
        
        # Set initial theme
        self.bg_color = self.dark_bg
        self.fg_color = self.dark_fg
        self.accent_color = self.dark_accent
        self.link_color = self.dark_link_color
        
        self.window.configure(bg=self.bg_color)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.update_button_style()
        
        # Main frame
        self.main_frame = tk.Frame(self.window, bg=self.bg_color)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Button frame
        button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        button_frame.pack(pady=10, fill='x')

        # Scrape button
        self.scrape_button = ttk.Button(button_frame, 
                                      text="Scrape Hacker News", 
                                      command=self.start_scraping)
        self.scrape_button.pack(side='left', padx=5)

        # Theme toggle button
        self.theme_button = ttk.Button(button_frame,
                                     text="Toggle Light/Dark",
                                     command=self.toggle_theme)
        self.theme_button.pack(side='left', padx=5)

        # Status label
        self.status_label = tk.Label(self.main_frame, 
                                   text="Ready",
                                   bg=self.bg_color,
                                   fg="#00cc00",
                                   font=("Open Sans", 10, "italic"))
        self.status_label.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame,
                                      mode='indeterminate',
                                      length=200)
        self.progress.pack(pady=5)

        # Result text area
        self.result_text = scrolledtext.ScrolledText(self.main_frame, 
                                                   width=90, 
                                                   height=30,
                                                   bg=self.accent_color,
                                                   fg=self.fg_color,
                                                   insertbackground=self.fg_color,
                                                   borderwidth=0,
                                                   relief="flat",
                                                   font=("Open Sans", 10))
        self.result_text.pack(pady=10, fill='both', expand=True)

        # Configure hyperlink tags
        self.update_link_style()
        self.result_text.tag_bind("link", "<Button-1>", self._open_link)
        self.result_text.tag_bind("link", "<Enter>", lambda e: self.result_text.config(cursor="hand2"))
        self.result_text.tag_bind("link", "<Leave>", lambda e: self.result_text.config(cursor=""))
        self.result_text.tag_bind("link", "<Button-3>", self._show_context_menu)

        # Context menu
        self.context_menu = Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Copy URL", command=self._copy_url)

        # Tooltips
        self.create_tooltips()

        self.window.mainloop()

    def update_button_style(self):
        self.style.configure('TButton',
                           background=self.accent_color,
                           foreground=self.fg_color,
                           borderwidth=0,
                           padding=5,
                           font=("Open Sans", 10))
        self.style.map('TButton',
                      background=[('active', '#5a5a5a' if self.dark_mode else '#d0d0d0')])

    def update_link_style(self):
        self.link_color = self.dark_link_color if self.dark_mode else self.light_link_color
        self.result_text.tag_configure("link",
                                     foreground=self.link_color,
                                     font=("Open Sans", 10, "bold"),
                                     underline=1)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.bg_color = self.dark_bg if self.dark_mode else self.light_bg
        self.fg_color = self.dark_fg if self.dark_mode else self.light_fg
        self.accent_color = self.dark_accent if self.dark_mode else self.light_accent
        
        self.window.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        self.status_label.configure(bg=self.bg_color, fg="#00cc00" if self.dark_mode else "#006600")
        self.result_text.configure(bg=self.accent_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.update_button_style()
        self.update_link_style()

    def create_tooltips(self):
        self.scrape_tip = ttk.Label(self.window, text="Click to scrape HN top stories", 
                                  background="#ffffe0", relief="solid", borderwidth=1,
                                  font=("Open Sans", 8))
        self.theme_tip = ttk.Label(self.window, text="Toggle between light/dark mode",
                                 background="#ffffe0", relief="solid", borderwidth=1,
                                 font=("Open Sans", 8))
        
        def show_tip(widget, tip, event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            tip.place(x=x, y=y)
        
        def hide_tip(tip, event):
            tip.place_forget()

        self.scrape_button.bind("<Enter>", lambda e: show_tip(self.scrape_button, self.scrape_tip, e))
        self.scrape_button.bind("<Leave>", lambda e: hide_tip(self.scrape_tip, e))
        self.theme_button.bind("<Enter>", lambda e: show_tip(self.theme_button, self.theme_tip, e))
        self.theme_button.bind("<Leave>", lambda e: hide_tip(self.theme_tip, e))

    def _open_link(self, event):
        index = self.result_text.index("@%s,%s" % (event.x, event.y))
        tags = self.result_text.tag_names(index)
        for tag in tags:
            if tag.startswith("url_"):
                url = tag[4:]
                webbrowser.open(url)
                break

    def _show_context_menu(self, event):
        index = self.result_text.index("@%s,%s" % (event.x, event.y))
        tags = self.result_text.tag_names(index)
        self.current_url = None
        for tag in tags:
            if tag.startswith("url_"):
                self.current_url = tag[4:]
                break
        if self.current_url:
            self.context_menu.post(event.x_root, event.y_root)

    def _copy_url(self):
        if self.current_url:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.current_url)

    def scrape_hn(self):
        try:
            self.status_label.config(text="Scraping in progress...")
            self.progress.start(10)
            self.window.update()

            res = requests.get('https://news.ycombinator.com/news')
            res2 = requests.get('https://news.ycombinator.com/news?p=2')
            soup = BeautifulSoup(res.text, 'html.parser')
            soup2 = BeautifulSoup(res2.text, 'html.parser')

            links = soup.select('.titleline > a')
            subtext = soup.select('.subtext')
            links2 = soup2.select('.titleline > a')
            subtext2 = soup2.select('.subtext')

            mega_links = links + links2
            mega_subtext = subtext + subtext2

            hn_list = self.create_custom_hn(mega_links, mega_subtext)

            self.result_text.delete(1.0, tk.END)

            for item in hn_list:
                self.result_text.insert(tk.END, f"Title: {item['title']}\n")
                url = item['link']
                self.result_text.insert(tk.END, "Link: ")
                url_tag = f"url_{url}"
                self.result_text.insert(tk.END, url, ("link", url_tag))
                self.result_text.insert(tk.END, "\n")
                self.result_text.insert(tk.END, f"Votes: {item['votes']}\n\n")

            self.progress.stop()
            self.status_label.config(text="Scraping completed!")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text=f"Error: {str(e)}")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"An error occurred: {str(e)}")

    def sort_stories_by_votes(self, hnlist):
        return sorted(hnlist, key=lambda k: k['votes'], reverse=True)

    def create_custom_hn(self, links, subtext):
        hn = []
        for idx, item in enumerate(links):
            title = item.getText()
            href = item.get('href', None)
            vote = subtext[idx].select('.score')
            if len(vote):
                points = int(vote[0].getText().replace(' points', ''))
                if points > 99:
                    if href.startswith('/'):
                        href = f"https://news.ycombinator.com{href}"
                    hn.append({'title': title, 'link': href, 'votes': points})
        return self.sort_stories_by_votes(hn)

    def start_scraping(self):
        thread = threading.Thread(target=self.scrape_hn)
        thread.start()

if __name__ == "__main__":
    app = HackerNewsScraper()