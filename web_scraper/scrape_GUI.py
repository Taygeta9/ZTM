import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext
import threading
import webbrowser

class HackerNewsScraper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hacker News Scraper")
        self.window.geometry("800x600")

        # Create GUI elements
        self.scrape_button = tk.Button(self.window, 
                                     text="Scrape Hacker News", 
                                     command=self.start_scraping)
        self.scrape_button.pack(pady=10)

        self.status_label = tk.Label(self.window, text="Ready")
        self.status_label.pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(self.window, 
                                                   width=90, 
                                                   height=30)
        self.result_text.pack(pady=10)

        # Configure tag for hyperlinks
        self.result_text.tag_configure("link", 
                                     foreground="purple", 
                                     underline=1)
        self.result_text.tag_bind("link", 
                                "<Button-1>", 
                                self._open_link)
        self.result_text.tag_bind("link", 
                                "<Enter>", 
                                lambda e: self.result_text.config(cursor="hand2"))
        self.result_text.tag_bind("link", 
                                "<Leave>", 
                                lambda e: self.result_text.config(cursor=""))

        self.window.mainloop()

    def _open_link(self, event):
        # Get the index of the click
        index = self.result_text.index("@%s,%s" % (event.x, event.y))
        # Get the tags at that index
        tags = self.result_text.tag_names(index)
        # Find the link tag that contains the URL
        for tag in tags:
            if tag.startswith("url_"):
                url = tag[4:]  # Remove "url_" prefix
                webbrowser.open(url)
                break

    def scrape_hn(self):
        try:
            self.status_label.config(text="Scraping in progress...")
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
                # Insert title
                self.result_text.insert(tk.END, f"Title: {item['title']}\n")
                
                # Insert clickable link
                url = item['link']
                self.result_text.insert(tk.END, "Link: ")
                # Create unique tag for each URL
                url_tag = f"url_{url}"
                self.result_text.insert(tk.END, url, ("link", url_tag))
                self.result_text.insert(tk.END, "\n")
                
                # Insert votes
                self.result_text.insert(tk.END, f"Votes: {item['votes']}\n\n")

            self.status_label.config(text="Scraping completed!")
            
        except Exception as e:
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
                    hn.append({'title': title, 'link': href, 'votes': points})
        return self.sort_stories_by_votes(hn)

    def start_scraping(self):
        thread = threading.Thread(target=self.scrape_hn)
        thread.start()

if __name__ == "__main__":
    app = HackerNewsScraper()