import tkinter as tk
from tkinter import filedialog, messagebox
import mmap
import re

class FastTextReader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast Text Reader")
        self.geometry("800x600")

        # Create menu
        self.create_menu()

        # Create search frame
        self.create_search_frame()

        # Create main content frame
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(expand=True, fill='both')

        # Create navigation slider
        self.create_navigation_slider()

        # Create text widget
        self.create_text_widget()

        # Create scrollbars
        self.create_scrollbars()

        # Search variables
        self.search_start = "1.0"
        self.last_search = None

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_search_frame(self):
        search_frame = tk.Frame(self)
        search_frame.pack(side=tk.TOP, fill=tk.X)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        search_button = tk.Button(search_frame, text="Search", command=self.search_next)
        search_button.pack(side=tk.LEFT)

        next_button = tk.Button(search_frame, text="Next", command=self.search_next)
        next_button.pack(side=tk.LEFT)

        prev_button = tk.Button(search_frame, text="Previous", command=self.search_previous)
        prev_button.pack(side=tk.LEFT)

    def create_navigation_slider(self):
        self.nav_slider = tk.Scale(self.content_frame, from_=0, to=100, orient=tk.VERTICAL, 
                                   command=self.on_nav_slider_move)
        self.nav_slider.pack(side=tk.LEFT, fill=tk.Y)

    def create_text_widget(self):
        self.text_widget = tk.Text(self.content_frame, wrap=tk.NONE)
        self.text_widget.pack(side=tk.LEFT, expand=True, fill='both')

    def create_scrollbars(self):
        self.v_scrollbar = tk.Scrollbar(self.content_frame, orient='vertical', command=self.text_widget.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.text_widget.configure(yscrollcommand=self.on_text_scroll)

        h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.text_widget.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill='x')
        self.text_widget.configure(xscrollcommand=h_scrollbar.set)

    def on_text_scroll(self, *args):
        self.v_scrollbar.set(*args)
        self.update_nav_slider()

    def update_nav_slider(self):
        first, last = self.text_widget.yview()
        self.nav_slider.set(first * 100)

    def on_nav_slider_move(self, value):
        self.text_widget.yview_moveto(float(value) / 100)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                    content = mmapped_file.read().decode('utf-8')
                    
                    self.text_widget.delete('1.0', tk.END)
                    self.text_widget.insert(tk.END, content)
                    mmapped_file.close()
                self.update_nav_slider()
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {e}")

    def search_next(self):
        search_term = self.search_var.get()
        if search_term == "":
            return

        if self.last_search != search_term:
            self.search_start = "1.0"
            self.last_search = search_term

        start_pos = self.search_start
        if start_pos == "1.0":
            start_pos = self.text_widget.index(start_pos)
        else:
            start_pos = self.text_widget.index(f"{start_pos}+1c")

        pos = self.text_widget.search(search_term, start_pos, stopindex=tk.END, regexp=True)
        if pos:
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_term)}"
            self.text_widget.tag_remove('search', '1.0', tk.END)
            self.text_widget.tag_add('search', pos, end_pos)
            self.text_widget.tag_config('search', background='yellow')
            self.text_widget.see(pos)
            self.search_start = end_pos
            self.update_nav_slider()
        else:
            messagebox.showinfo("Search Result", "No more occurrences found.")
            self.search_start = "1.0"

    def search_previous(self):
        search_term = self.search_var.get()
        if search_term == "":
            return

        if self.last_search != search_term:
            self.search_start = tk.END
            self.last_search = search_term

        end_pos = self.text_widget.index(f"{self.search_start}-1c")
        pos = self.text_widget.search(search_term, "1.0", stopindex=end_pos, regexp=True, backwards=True)
        
        if pos:
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_term)}"
            self.text_widget.tag_remove('search', '1.0', tk.END)
            self.text_widget.tag_add('search', pos, end_pos)
            self.text_widget.tag_config('search', background='yellow')
            self.text_widget.see(pos)
            self.search_start = pos
            self.update_nav_slider()
        else:
            messagebox.showinfo("Search Result", "No more occurrences found.")
            self.search_start = tk.END

if __name__ == "__main__":
    app = FastTextReader()
    app.mainloop()