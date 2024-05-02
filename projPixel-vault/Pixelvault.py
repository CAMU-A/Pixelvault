import random
import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image
import cv2
from ttkthemes import ThemedStyle

root = tk.Tk()

root.title("PixelVault")

root.iconbitmap(r'steg.ico')

style = ThemedStyle(root)
style.set_theme("equilux")

frame = ttk.Frame(root, padding=0)
frame.grid(row=0, column=0, padx=0, pady=0)

input_text = tk.Text(frame, height=10, width=40, bg='gray',
                     font=("Helvetica", 12), border=10, relief='flat')
input_text.grid(row=0, column=0, padx=10, pady=10)

posschar = string.digits \
           + string.ascii_letters \
           + string.punctuation \
           + string.ascii_uppercase \
           + string.ascii_lowercase\
           + string.whitespace
charmap = list(posschar)
coordsx = []
coordsy = []


def encode_text():
    text = input_text.get("1.0", "end-1c")
    letters = []
    if len(text) > 32:
        tk.messagebox.showerror("Error",
                                "The entered text is too lengthy. "
                                "Please provide a shorter input.")
        return

    for i in range(len(text)):
        char = text[i]

        if char not in charmap:
            tk.messagebox.showerror("Error:Unsupported character",
                                    "Please enter a valid character.")
            print(f"Unsupported character: {char}")
            return

        n = charmap.index(char)

        if n is not None:

            randomX = random.randint(1, 254)
            randomY = random.randint(1, 254)

            while (randomX, randomY) in coordsx or (randomX, randomY) in coordsy:
                randomX = random.randint(1, 253)
                randomY = random.randint(1, 253)

            coordsx.append(randomX)
            coordsy.append(randomY)

            letters.append(n)

        else:
            tk.messagebox.showerror('FAILED', 'Sorry\n Encoding failed'
                                              '. Please try again')
            return

    img = np.zeros([256, 256, 3], dtype=np.uint8)

    for i in range(256):
        for j in range(256):
            img[i, j] = (25, 24, 32)

    img[0, 0] = (28, 24, 32)
    img[0, 1] = (25, 24, 27)

    currentX = 0
    for i in range(len(letters)):
        coordStringX = str(coordsx[i])
        coordStringY = str(coordsy[i])

        for j in range(len(coordStringX)):
            img[254, 255 - currentX - j] = (int(coordStringX[j]), 24, 32)

        for j in range(len(coordStringY)):
            img[255, 255 - currentX - j] = (int(coordStringY[j]), 24, 32)

        img[254, 255 - currentX - len(coordStringX)] = (24, 23, 32)
        img[255, 255 - currentX - len(coordStringY)] = (24, 23, 32)

        currentX += len(coordStringX) + len(coordStringY) + 2
    for i in range(len(letters)):
        img[coordsy[i], coordsx[i]] = (letters[i], 24, 32)

    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")])
    if file_path:
        img_path = file_path
        Image.fromarray(img).save(img_path)

        tk.messagebox.showinfo("Success",
                               f"Image saved successfully as {img_path}")
        print(f'successfully saved the image as {img_path}')


def decode_text():
    coordsx.clear()
    coordsy.clear()

    file_path = filedialog.askopenfilename(filetypes=[("Image files",
                                                       "*.png")])
    if not file_path:
        tk.messagebox.showwarning("Aborted.",
                                  "Decoding was aborted.")
        return

    img = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
    if img.shape != (256, 256, 3):
        tk.messagebox.showerror("Error: Unidentified image",
                                "The provided image is not a pixelVault generated image.")
        return
    if tuple(img[0, 0]) != (28, 24, 32) or tuple(img[0, 1]) != (25, 24, 27):
        tk.messagebox.showerror("Error: Unauthentic image",
                                "The provided image is not an authentic "
                                "pixelVault generated image.")
        return

    try:
        currentX = 0
        while True:
            coordStringX = ''
            coordStringY = ''
            if tuple(img[254, 255 - currentX]) == (25, 24, 32):
                break
            for i in range(255):
                if tuple(img[254, 255 - currentX - i]) == (24, 23, 32):
                    break
                coordStringX += str(img[254, 255 - currentX - i][0])
            for i in range(255):
                if tuple(img[255, 255 - currentX - i]) == (24, 23, 32):
                    break
                coordStringY += str(img[255, 255 - currentX - i][0])
            if not coordStringX or not coordStringY:
                break
            coordsx.append(int(coordStringX))
            coordsy.append(int(coordStringY))
            currentX += len(coordStringX) + len(coordStringY) + 2

    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to decode.\n {e}")
        return

    decoded = []
    for i in range(len(coordsx)):
        char = img[coordsy[i], coordsx[i]][0]
        if char > len(charmap):
            decoded.append('\x00')
        else:
            decoded.append(charmap[char])

    decoded_text = ''.join(decoded)
    output_file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt")])
    if output_file_path:
        with open(output_file_path, 'w') as f:
            f.write(decoded_text)
        result_label.config(text=f"Saved as {output_file_path}")
        tk.messagebox.showinfo("Saved successfully",f"The decoded message is saved successfully as a text file at {output_file_path}")


encode_button = ttk.Button(frame, text="Encrypt", command=encode_text)
encode_button.grid(row=1, column=0, padx=10, pady=10)

decode_button = ttk.Button(frame, text="Decrypt", command=decode_text)
decode_button.grid(row=2, column=0, padx=10, pady=10)

result_label = ttk.Label(frame, text="", wraplength=400)
result_label.grid(row=3, column=0, padx=10, pady=10)

root.mainloop()




