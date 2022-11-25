"""
Gui for view image.
"""

import os
import subprocess
import threading
import tkinter
from datetime import datetime
from functools import partial

import cfg
import cv2
import sqlalchemy
from database import Dbase, Thumbs
from PIL import ImageTk
from utils import (MyButton, MyFrame, MyLabel, convert_to_rgb, decode_image,
                   get_coll_name, my_copy, place_center, resize_image,
                   smb_check)

from .ask_exit import AskExit
from .images_compare import ImagesCompare
from .smb_checker import SmbChecker

vars = {
    'img_src': os.PathLike,
    'all_src': [],
    'height': 0,
    'width': 0,
    'img_info': tkinter.Label,
    'img_frame': tkinter.Label,
    'curr_img': ImageTk
    }


def pack_widgets(win: tkinter.Toplevel):
    ImgSrc(win)
    
    image_frame = ImageFrame(win)
    image_frame.pack(expand=True, fill=tkinter.BOTH)

    left_frame = MyFrame(win)
    left_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)
    prev_img = PrevItem(left_frame)
    prev_img.pack(expand=True, fill=tkinter.X)

    center_frame = MyFrame(win)
    center_frame.pack(side=tkinter.LEFT, fill=tkinter.X)
    img_btns = ImgButtons(center_frame)
    img_btns.pack(pady=(15, 15))
    img_info = ImgInfo(center_frame)
    img_info.pack(pady=(0, 15), padx=15, expand=True, fill=tkinter.X)
    close = CloseButton(center_frame)
    close.pack()

    right_frame = MyFrame(win, bg='red')
    right_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)
    next_img = NextItem(right_frame)
    next_img.pack(expand=True, fill=tkinter.X)

    if vars['height'] == 0:
        center_frame.update_idletasks()
        vars['height'] = image_frame.winfo_height()
        vars['width'] = win.winfo_width()
        image_frame.set_size()

    image_frame.place_thumbnail()


def on_closing(window: tkinter.Toplevel):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """
    window.destroy()
    cfg.ROOT.focus_force()


def load_image():
    t1 = threading.Thread(target=vars['img_frame'].place_image)
    t1.start()
    while t1.is_alive():
        cfg.ROOT.update()


def switch_image(master: tkinter.Toplevel, index: int):
    try:
        vars['img_src'] = vars['all_src'][index]
    except IndexError:
        vars['img_src'] = vars['all_src'][0]
    master = master.winfo_toplevel()
    for i in master.winfo_children():
        i.destroy()
    pack_widgets(master)
    load_image()


class ImagePreview(tkinter.Toplevel):
    """
    Creates new window (tkinter Top Level) with image & buttons.
    * param `src`: source path of image.
    """
    def __init__(self, src, all_src):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        if not smb_check():
            on_closing(self)
            SmbChecker()
            return

        if src is None:
            on_closing(self)
            return

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Escape>', lambda e: on_closing(self))
        self.bind('<Command-q>', lambda e: AskExit(cfg.ROOT))
        self.title('Просмотр')
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        vars['img_src'] = src
        vars['all_src'] = all_src

        pack_widgets(self)
        cfg.ROOT.update_idletasks()

        if cfg.COMPARE:
            load_image()
            ImagesCompare()
            return

        place_center(self)
        self.deiconify()
        self.grab_set()
        load_image()


class ImgSrc(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text=vars['img_src'])


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        vars['img_frame'] = self
        self['bg']='black'
        self.bind('<ButtonRelease-1>', lambda e: self.next_image(e))

    def next_image(self, e: tkinter.Event):
        if e.x <= vars['width']//2:
            index = vars['all_src'].index(vars['img_src']) - 1
        else:
            index = vars['all_src'].index(vars['img_src']) + 1
        switch_image(self, index)

    def set_size(self):
        self['height'] = vars['height']
        self['width'] = vars['width']

    def place_thumbnail(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src == vars['img_src'])).first()[0]
        decoded = decode_image(thumb)
        resized = resize_image(decoded, vars['width'], vars['height'], False)
        rgb_image = convert_to_rgb(resized)

        img_tk = ImageTk.PhotoImage(rgb_image)
        self.configure(image=img_tk)
        self.image = img_tk

    def place_image(self):
        img_read = cv2.imread(vars['img_src'])
        resized = resize_image(img_read, vars['width'], vars['height'], False)
        vars['curr_img'] = convert_to_rgb(resized)
        img_tk = ImageTk.PhotoImage(vars['curr_img'])
        self.configure(image=img_tk)
        self.image = img_tk
        t = vars['img_info']['text']
        h, w = img_read.shape[:2]
        vars['img_info']['text'] = t.replace('Загрузка', f'{w} x {h}')


class ImgInfo(MyLabel):
    """
    Creates tkinter frame.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master)
        vars['img_info'] = self

        name = vars['img_src'].split(os.sep)[-1]
        path = vars["img_src"].replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = path.replace(cfg.config["PHOTO_DIR"], "Фото")
        filesize = round(os.path.getsize(vars['img_src'])/(1024*1024), 2)
        filemod = datetime.fromtimestamp(os.path.getmtime(vars['img_src']))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        txt = (f'Коллекция: {get_coll_name(vars["img_src"])}'
                f'\nИмя: {name}'
                f'\nПуть: {path}'
                f'\nРазрешение: Загрузка'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        self.configure(
            text=txt, justify=tkinter.LEFT, anchor=tkinter.W, width=43)

class ImgButtons(MyFrame):
    """
    Tkinter frame with button that calls images compare method.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        comp_btn = MyButton(self, text='Сравнить')
        comp_btn.configure(height=1, width=b_wight)
        comp_btn.cmd(lambda e: self.compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)

        if os.path.exists(vars['img_src']):
            open_btn = MyButton(self, text='Открыть папку')
            open_btn.configure(height=1, width=b_wight)
            open_btn.cmd(partial(self.open_folder, open_btn))
            open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def compare(self, btn: MyButton):
        """
        Compares two images and open gui with result.
        * param `btn`: current tkinter button.
        """
        btn.press()
        if not cfg.COMPARE:
            cfg.STATUSBAR_COMPARE()
            for i in cfg.THUMBS:
                if i['text'] == vars['img_src']:
                    i['bg'] = cfg.BGPRESSED
                    break
            win = self.winfo_toplevel()
            win.withdraw()
            win.grab_release()
            cfg.COMPARE = True
            return

    def copy_name(self, btn: MyButton):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        my_copy(vars['img_src'].split(os.sep)[-1].split('.')[0])

    def open_folder(self, btn: MyButton, e: tkinter.Event):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = os.sep.join(vars['img_src'].split(os.sep)[:-1])

        def open():
            subprocess.check_output(["/usr/bin/open", path])

        threading.Thread(target=open).start()


class CloseButton(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=1, width=13)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))


class NextItem(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='•', font=('Arial', 22, 'bold'))
        self.configure(bg=cfg.BGCOLOR)
        self.winfo_toplevel().bind('<Right>', lambda e: self.next_img())
        self.cmd(lambda e: self.next_img())
        self.unbind('<Enter>')
        self.unbind('<Leave>')

    def next_img(self):
        index = vars['all_src'].index(vars['img_src']) + 1
        switch_image(self, index)


class PrevItem(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='•', font=('Arial', 22, 'bold'))
        self.configure(bg=cfg.BGCOLOR)
        self.winfo_toplevel().bind('<Left>', lambda e: self.prev_img())
        self.cmd(lambda e: self.prev_img())
        self.unbind('<Enter>')
        self.unbind('<Leave>')

    def prev_img(self):
        index = vars['all_src'].index(vars['img_src']) - 1
        switch_image(self, index)
