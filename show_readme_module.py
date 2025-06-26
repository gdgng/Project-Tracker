import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
from PIL import Image, ImageTk


class MarkdownViewer(tk.Tk):

    def __init__(self):
        super().__init__()
        self.image_refs = []  # Houd referenties naar afbeeldingen vast
        self.title("README.md Viewer")
        self.geometry("900x700")
        self.minsize(900, 700)
        self.current_file = None
        self.setup_ui()
        self.auto_load_readme()

    def setup_ui(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        # file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")  # Hidden
        # file_menu.add_command(label="Reload", command=self.reload_file, accelerator="F5")  # Hidden
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        toolbar = tk.Frame(self, relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Hiding Open and Reload buttons
        # open_btn = tk.Button(toolbar, text="Open File", command=self.open_file)
        # open_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # reload_btn = tk.Button(toolbar, text="Reload", command=self.reload_file)
        # reload_btn.pack(side=tk.LEFT, padx=2, pady=2)

        self.file_label = tk.Label(toolbar, text="No file loaded", fg="gray")
        self.file_label.pack(side=tk.LEFT, padx=10, pady=2)

        self.text_display = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="white",
            fg="black",
            padx=10,
            pady=10
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.configure_text_tags()

        self.status_bar = tk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Remove keyboard shortcuts for hidden features
        # self.bind('<Control-o>', lambda e: self.open_file())
        # self.bind('<F5>', lambda e: self.reload_file())

    def configure_text_tags(self):
        self.text_display.tag_configure("h1", font=("Arial", 18, "bold"), spacing1=10, spacing3=5)
        self.text_display.tag_configure("h2", font=("Arial", 16, "bold"), spacing1=8, spacing3=4)
        self.text_display.tag_configure("h3", font=("Arial", 14, "bold"), spacing1=6, spacing3=3)
        self.text_display.tag_configure("h4", font=("Arial", 12, "bold"), spacing1=4, spacing3=2)
        self.text_display.tag_configure("bold", font=("Consolas", 11, "bold"))
        self.text_display.tag_configure("italic", font=("Consolas", 11, "italic"))
        self.text_display.tag_configure("code_inline", font=("Courier", 10), background="#f0f0f0")
        self.text_display.tag_configure("code_block", font=("Courier", 10), background="#f8f8f8", relief=tk.SOLID, borderwidth=1, lmargin1=20, lmargin2=20, spacing1=5, spacing3=5)
        self.text_display.tag_configure("list_item", lmargin1=20, lmargin2=30)
        self.text_display.tag_configure("link", foreground="blue", underline=True)
        self.text_display.tag_configure("blockquote", lmargin1=20, lmargin2=20, background="#f9f9f9", relief=tk.SOLID, borderwidth=1)

    def auto_load_readme(self):
        readme_files = ["README.md", "readme.md", "Readme.md", "README.MD"]
        for filename in readme_files:
            if os.path.exists(filename):
                self.load_file(filename)
                break

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.current_file = file_path
            self.file_label.config(text=f"File: {os.path.basename(file_path)}", fg="black")
            self.status_bar.config(text=f"Loaded: {file_path}")
            self.text_display.delete(1.0, tk.END)
            self.render_markdown(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            self.status_bar.config(text="Error loading file")

    def render_markdown(self, content):
        lines = content.split('\n')
        in_code_block = False
        code_block_content = []
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    if code_block_content:
                        code_text = '\n'.join(code_block_content) + '\n'
                        self.text_display.insert(tk.END, code_text, "code_block")
                        code_block_content = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue
            if in_code_block:
                code_block_content.append(line)
                continue
            self.process_markdown_line(line)

    def process_markdown_line(self, line):
        if line.startswith('# '):
            self.text_display.insert(tk.END, line[2:] + '\n', "h1")
        elif line.startswith('## '):
            self.text_display.insert(tk.END, line[3:] + '\n', "h2")
        elif line.startswith('### '):
            self.text_display.insert(tk.END, line[4:] + '\n', "h3")
        elif line.startswith('#### '):
            self.text_display.insert(tk.END, line[5:] + '\n', "h4")
        elif line.startswith('> '):
            self.text_display.insert(tk.END, line[2:] + '\n', "blockquote")
        elif line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\s*\d+\.\s', line):
            self.text_display.insert(tk.END, line + '\n', "list_item")
        elif re.match(r'!\[.*?\]\(.*?\)', line.strip()):
            self.render_image_from_markdown(line.strip())
        else:
            self.process_inline_formatting(line + '\n')

    def process_inline_formatting(self, text):
        remaining_text = text
        remaining_text = re.sub(r'\*\*(.*?)\*\*', r'[\1]BOLD', remaining_text)
        remaining_text = re.sub(r'\*(.*?)\*', r'[\1]ITALIC', remaining_text)
        remaining_text = re.sub(r'`(.*?)`', r'[\1]CODE', remaining_text)
        remaining_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'[\1]LINK', remaining_text)
        self.text_display.insert(tk.END, text)


    def render_image_from_markdown(self, line):
        match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
        if match:
            alt_text, image_path = match.groups()
            full_path = os.path.join(os.path.dirname(__file__), image_path)
            if os.path.exists(full_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(full_path)
                    img.thumbnail((800, 600))  # Pas grootte aan indien nodig
                    img_tk = ImageTk.PhotoImage(img)
                    image_label = tk.Label(self.text_display, image=img_tk)
                    image_label.image = img_tk
                    self.image_refs.append(img_tk)
                    # Bewaar referentie!
                    self.text_display.window_create(tk.END, window=image_label)
                    self.text_display.insert(tk.END, "\n")  # Extra newline
                except Exception as e:
                    self.text_display.insert(tk.END, f"[Error loading image: {alt_text}]\n")
            else:
                self.text_display.insert(tk.END, f"[Image not found: {alt_text}]\n")

# Run the application
if __name__ == "__main__":
    app = MarkdownViewer()
    app.mainloop()
