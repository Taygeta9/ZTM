import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# Dark Mode Colors
BG_COLOR = "#1e1e1e"  # Dark background
FG_COLOR = "#ffa500"  # Orange text
BUTTON_COLOR = "#333333"  # Dark gray button
BUTTON_TEXT = "#ffffff"  # White button text

def resize_and_compress(input_path, output_path, format="jpg", size=(500, 500), quality=80):
    """Resize and compress an image for web optimization."""
    try:
        with Image.open(input_path) as img:
            img = img.resize(size, Image.LANCZOS)
            img = img.convert("RGB")

            if format == "webp":
                img.save(output_path, "WEBP", optimize=True, quality=quality)
            else:
                img.save(output_path, "JPEG", optimize=True, quality=quality)

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
            raise ValueError("Width and height must be positive numbers!")
    except ValueError as e:
        messagebox.showerror("Error", str(e) if str(e) != "" else "Please enter valid numbers for width and height!")
        return

    file_types = [("JPEG Files", "*.jpg"), ("WebP Files", "*.webp")]
    file_ext = "jpg" if format_var.get() == "jpg" else "webp"
    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_ext}", filetypes=file_types)

    if file_path:
        selected_size = (width, height)
        resize_and_compress(input_path.get(), file_path, format_var.get(), selected_size)

# GUI Setup
root = tk.Tk()
root.title("Image Resizer & Compressor")
root.geometry("420x300")  # Adjusted height for new controls
root.config(bg=BG_COLOR)

input_path = tk.StringVar()
format_var = tk.StringVar(value="jpg")
width_var = tk.StringVar(value="500")
height_var = tk.StringVar(value="500")

# Labels and Input
tk.Label(root, text="Select an image:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
tk.Entry(root, textvariable=input_path, width=40, state="readonly", bg=BUTTON_COLOR, fg=FG_COLOR).pack(pady=5)
tk.Button(root, text="Browse", command=open_file, bg=BUTTON_COLOR, fg=BUTTON_TEXT).pack(pady=5)

# Size Selection
tk.Label(root, text="Enter output size (pixels):", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
size_frame = tk.Frame(root, bg=BG_COLOR)
size_frame.pack(pady=5)

tk.Label(size_frame, text="Width:", fg=FG_COLOR, bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
tk.Entry(size_frame, textvariable=width_var, width=10, bg=BUTTON_COLOR, fg=FG_COLOR).pack(side=tk.LEFT)

tk.Label(size_frame, text="Height:", fg=FG_COLOR, bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
tk.Entry(size_frame, textvariable=height_var, width=10, bg=BUTTON_COLOR, fg=FG_COLOR).pack(side=tk.LEFT)

# Format Selection
tk.Label(root, text="Select format:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 11)).pack(pady=5)
tk.Radiobutton(root, text="JPEG", variable=format_var, value="jpg", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()
tk.Radiobutton(root, text="WebP", variable=format_var, value="webp", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BUTTON_COLOR).pack()

tk.Button(root, text="Save Image", command=save_file, bg=BUTTON_COLOR, fg=BUTTON_TEXT).pack(pady=10)

root.mainloop()