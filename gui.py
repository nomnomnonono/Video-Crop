import argparse
import os
import tkinter as tk
from tkinter import messagebox

from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk

RESIZE_RETIO = 1.5
TMP_IMG = "tmp.png"


def start_point_get(event):
    global start_x, start_y

    canvas1.delete("rect1")

    canvas1.create_rectangle(event.x,
                             event.y,
                             event.x + 1,
                             event.y + 1,
                             outline="red",
                             tag="rect1")
    start_x, start_y = event.x, event.y


def rect_drawing(event):
    if event.x < 0:
        end_x = 0
    else:
        end_x = min(img_resized.width, event.x)
    if event.y < 0:
        end_y = 0
    else:
        end_y = min(img_resized.height, event.y)

    canvas1.coords("rect1", start_x, start_y, end_x, end_y)


def release_action(event):
    global start_x, start_y, end_x, end_y
    start_x, start_y, end_x, end_y = [
        round(n * RESIZE_RETIO) for n in canvas1.coords("rect1")
    ]

    if messagebox.askquestion("確認", "クロップ位置の確認") == "yes":
        root.destroy()


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_video",
        type=str,
        help="File path for input video.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="Directory path for output video.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = argparser()
    os.makedirs(args.output_dir, exist_ok=True)
    video = VideoFileClip(args.input_video).subclip(0, 60)
    video.save_frame(filename=TMP_IMG, t=10)
    img = Image.open(TMP_IMG)
    img_resized = img.resize(size=(int(img.width / RESIZE_RETIO),
                                   int(img.height / RESIZE_RETIO)),
                                   resample=Image.BILINEAR)

    root = tk.Tk()
    root.attributes("-topmost", True)

    img_tk = ImageTk.PhotoImage(img_resized, master=root)
    canvas1 = tk.Canvas(root,
                        bg="black",
                        width=img_resized.width,
                        height=img_resized.height)
    canvas1.create_image(0, 0, image=img_tk, anchor=tk.NW)

    canvas1.pack()

    canvas1.bind("<ButtonPress-1>", start_point_get)
    canvas1.bind("<Button1-Motion>", rect_drawing)
    canvas1.bind("<ButtonRelease-1>", release_action)

    root.mainloop()

    video = (video.crop(x1=start_x, y1=start_y, x2=end_x, y2=end_y))
    video.write_videofile(os.path.join(args.output_dir, os.path.split(args.input_video)[-1]), fps=video.fps)
