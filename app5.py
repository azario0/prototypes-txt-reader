import tkinter as tk
from tkinter import filedialog, messagebox
import mmap


class LineNumberedText(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.text = tk.Text(self, wrap=tk.NONE)
        self.linenumbers = tk.Text(self, width=4, padx=4, takefocus=0, border=0, 
                                   background='lightgrey', state='disabled')
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.linenumbers.tag_configure('line', justify='right')
        self.text.bind('<KeyPress>', self.on_key_press)
        self.text.bind('<KeyRelease>', self.on_key_release)

        self.update_line_numbers()

    def on_key_press(self, event):
        self.update_line_numbers()

    def on_key_release(self, event):
        self.update_line_numbers()

    def update_line_numbers(self):
        self.linenumbers.config(state='normal')
        self.linenumbers.delete('1.0', tk.END)
        num_lines = int(self.text.index(tk.END).split('.')[0]) - 1
        line_numbers_string = '\n'.join(str(i) for i in range(1, num_lines + 1))
        self.linenumbers.insert('1.0', line_numbers_string)
        self.linenumbers.config(state='disabled')
        
        # Adjust width of line numbers widget
        width = len(str(num_lines))
        if self.linenumbers.cget('width') != width:
            self.linenumbers.config(width=width)

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

        # Create text widget with line numbers
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
        self.text_widget = LineNumberedText(self.content_frame)
        self.text_widget.pack(side=tk.LEFT, expand=True, fill='both')

    def create_scrollbars(self):
        self.v_scrollbar = tk.Scrollbar(self.content_frame, orient='vertical', command=self.text_widget.text.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.text_widget.text.configure(yscrollcommand=self.on_text_scroll)

        h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.text_widget.text.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill='x')
        self.text_widget.text.configure(xscrollcommand=h_scrollbar.set)

    def on_text_scroll(self, *args):
        self.v_scrollbar.set(*args)
        self.update_nav_slider()
        self.text_widget.linenumbers.yview_moveto(args[0])

    def update_nav_slider(self):
        first, last = self.text_widget.text.yview()
        self.nav_slider.set(first * 100)

    def on_nav_slider_move(self, value):
        self.text_widget.text.yview_moveto(float(value) / 100)
        self.text_widget.linenumbers.yview_moveto(float(value) / 100)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                    content = mmapped_file.read().decode('utf-8')
                    
                    self.text_widget.text.delete('1.0', tk.END)
                    self.text_widget.text.insert(tk.END, content)
                    mmapped_file.close()
                self.text_widget.update_line_numbers()
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
            start_pos = self.text_widget.text.index(start_pos)
        else:
            start_pos = self.text_widget.text.index(f"{start_pos}+1c")

        pos = self.text_widget.text.search(search_term, start_pos, stopindex=tk.END, regexp=True)
        if pos:
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_term)}"
            self.text_widget.text.tag_remove('search', '1.0', tk.END)
            self.text_widget.text.tag_add('search', pos, end_pos)
            self.text_widget.text.tag_config('search', background='yellow')
            self.text_widget.text.see(pos)
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

        end_pos = self.text_widget.text.index(f"{self.search_start}-1c")
        pos = self.text_widget.text.search(search_term, "1.0", stopindex=end_pos, regexp=True, backwards=True)
        
        if pos:
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_term)}"
            self.text_widget.text.tag_remove('search', '1.0', tk.END)
            self.text_widget.text.tag_add('search', pos, end_pos)
            self.text_widget.text.tag_config('search', background='yellow')
            self.text_widget.text.see(pos)
            self.search_start = pos
            self.update_nav_slider()
        else:
            messagebox.showinfo("Search Result", "No more occurrences found.")
            self.search_start = tk.END

if __name__ == "__main__":
    app = FastTextReader()
    app.mainloop()