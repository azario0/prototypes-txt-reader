import tkinter as tk
from tkinter import filedialog, messagebox
import mmap

class FastTextReader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast Text Reader")
        self.geometry("800x600")

        # Create menu
        self.create_menu()

        # Create text widget
        self.text_widget = tk.Text(self, wrap=tk.NONE)
        self.text_widget.pack(expand=True, fill='both')

        # Create scrollbars
        self.create_scrollbars()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_scrollbars(self):
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(self, orient='vertical', command=self.text_widget.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.text_widget.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.text_widget.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill='x')
        self.text_widget.configure(xscrollcommand=h_scrollbar.set)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    # Use memory mapping for efficient reading of large files
                    mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                    content = mmapped_file.read().decode('utf-8')
                    
                    self.text_widget.delete('1.0', tk.END)
                    self.text_widget.insert(tk.END, content)
                    mmapped_file.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {e}")

if __name__ == "__main__":
    app = FastTextReader()
    app.mainloop()