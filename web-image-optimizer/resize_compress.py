import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

# Dark Mode Colors
BG_COLOR = "#1e1e1e"  # Dark background
FG_COLOR = "#ffa500"  # Orange text
BUTTON_COLOR = "#333333"  # Dark gray button
BUTTON_TEXT = "#ffffff"  # White button text

def resize_and_compress(input_path, output_path, format="jpg", size=(500, 500), quality=80):
    """Resize and compress an image."""
    try:
        with Image.open(input_path) as img:
            img = img.resize(size, Image.LANCZOS)
            
            if format in ["jpg", "webp"]:
                img = img.convert("RGB")
            elif format in ["png", "ico"]:
                img = img.convert("RGBA")

            if format == "webp":
                img.save(output_path, "WEBP", optimize=True, quality=quality)
            elif format == "jpg":
                img.save(output_path, "JPEG", optimize=True, quality=quality)
            elif format == "png":
                img.save(output_path, "PNG", optimize=True)
            elif format == "ico":
                img.save(output_path, "ICO")

        messagebox.showinfo("Success", f"Image saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_file():
    """Open file dialog to select an image."""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp")])
    if file_path:
        input_path.set(file_path)

def save_file():
    """Save file dialog to select output location."""
    if not input_path.get():
        messagebox.showerror("Error", "Please select an image first!")
        return
    
    try:
        width = int(width_var.get())
        height = int(height_var.get())
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive numbers!")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid width and height values!")
        return

    file_types = [
        ("JPEG Files", "*.jpg"),
        ("WebP Files", "*.webp"),
        ("PNG Files", "*.png"),
        ("ICO Files", "*.ico")
    ]
    file_ext = format_var.get()
    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_ext}", filetypes=file_types)

    if file_path:
        resize_and_compress(input_path.get(), file_path, format_var.get(), (width, height))

# GUI Setup
root = tk.Tk()
root.title("Image Resizer")
root.geometry("420x360")
root.config(bg=BG_COLOR)

input_path = tk.StringVar()
format_var = tk.StringVar(value="jpg")
width_var = tk.StringVar(value="500")
height_var = tk.StringVar(value="500")

# Input Section
tk.Label(root, text="Select an image:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
tk.Entry(root, textvariable=input_path, width=40, state="readonly", bg=BUTTON_COLOR, fg=FG_COLOR).pack(pady=5)
tk.Button(root, text="Browse", command=open_file, bg=BUTTON_COLOR, fg=BUTTON_TEXT).pack(pady=5)

# Size Section
tk.Label(root, text="Image Size (pixels):", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
size_frame = tk.Frame(root, bg=BG_COLOR)
size_frame.pack(pady=5)
tk.Label(size_frame, text="Width:", fg=FG_COLOR, bg=BG_COLOR).pack(side=tk.LEFT)
tk.Entry(size_frame, textvariable=width_var, width=10, bg=BUTTON_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=5)
tk.Label(size_frame, text="Height:", fg=FG_COLOR, bg=BG_COLOR).pack(side=tk.LEFT)
tk.Entry(size_frame, textvariable=height_var, width=10, bg=BUTTON_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=5)

# Format Section
tk.Label(root, text="Select format:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
tk.Radiobutton(root, text="JPEG", variable=format_var, value="jpg", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()
tk.Radiobutton(root, text="WebP", variable=format_var, value="webp", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()
tk.Radiobutton(root, text="PNG", variable=format_var, value="png", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()
tk.Radiobutton(root, text="ICO", variable=format_var, value="ico", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()

# Save Button
tk.Button(root, text="Save Image", command=save_file, bg=BUTTON_COLOR, fg=BUTTON_TEXT).pack(pady=10)

root.mainloop()