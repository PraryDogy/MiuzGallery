"""
Tkinter toplevel gui with app settings.
"""

import json
import os
import sys
import tkinter
from tkinter.ttk import Separator

import cfg
import sqlalchemy
import tkmacosx
from database import Config, Dbase
from PIL import Image, ImageTk
from Utils.Styled import MyButton, MyFrame, MyLabel
from Utils.Utils import my_copy, my_paste

from .descriptions import descriptions


class Globals:
    """
    Stores global variables.
    """
    gen_frame = tkinter.Frame
    adv_frame = tkinter.Frame
    gen_btn = tkinter.Button
    adv_btn = tkinter.Button
    save_close = tkinter.Frame
    inserts = []


class Settings(tkinter.Toplevel):
    """
    Tkinter toplevel with settings gui.
    """

    def __init__(self):
        tkinter.Toplevel.__init__(self, cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')

        self.withdraw()
        self.resizable(0,0)
        self.title('Настройки')
        self.geometry('570x650')
        self.configure(padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        frame_up = MyFrame(self)
        frame_up.pack(fill=tkinter.BOTH, expand=True)

        frame_bott = MyFrame(self)
        frame_bott.pack()

        LeftMenu(frame_up).pack(side=tkinter.LEFT, padx=(0, 10))

        General(frame_up).pack(fill=tkinter.BOTH, expand=True)
        Expert(frame_up)

        BelowMenu(frame_bott).pack(pady=(10,0))

        cfg.ROOT.update_idletasks()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
        xx = x + int(cfg.ROOT.winfo_width()/2)-int(self.winfo_width()/2)
        yy = y + int(cfg.ROOT.winfo_height()/2)-int(self.winfo_height()/2)

        self.geometry(f'+{xx}+{yy}')
        self.deiconify()
        self.grab_set()

    def on_closing(self):
        """
        Close tkinter toplevel window.
        Change global variable cfg.TOP_LVL to False.
        cfg.TOP_LVL prevents creating new window with settings while True.
        """
        self.destroy()


class LeftMenu(MyFrame):
    """
    Menu with buttons "General settins" and "Advanced settings".
    param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        Globals.gen_btn = MyButton(self, text='Основные')
        Globals.gen_btn.configure(bg=cfg.BGPRESSED)

        Globals.gen_btn.Cmd(lambda e: self.change(
            kill=Globals.adv_frame, pack=Globals.gen_frame,
            press=Globals.gen_btn, clear=Globals.adv_btn))
        Globals.gen_btn.pack()

        Globals.adv_btn = MyButton(self, text = 'Дополнительно')

        Globals.adv_btn.Cmd(lambda e: self.change(
            kill=Globals.gen_frame, pack=Globals.adv_frame,
            press=Globals.adv_btn, clear=Globals.gen_btn))
        Globals.adv_btn.pack()

    def change(self, **kw):
        """
        Destroys frame, creates new one.
        Press button with created frame and clear button with destroyed frame.

        * params: `kill`, `pack`, `press`, `clear`
        * param `kill`: tkinter frame for destroy
        * param `pack`: tkinter frame for pack: fill both, expand is True
        * param `press`: changes tkinter button bg to cfg.BGPRESSED
        * param `clear`: changes tkinter button bg to cfg.BGBUTTON
        """
        kw['kill'].pack_forget()
        kw['pack'].pack(fill=tkinter.BOTH, expand=True)

        kw['press'].configure(bg=cfg.BGPRESSED)
        kw['clear'].configure(bg=cfg.BGBUTTON)


class BelowMenu(MyFrame):
    """
    Creates tkinter frame with save settings button and close button.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        Globals.save_close = self

        save_btn = MyButton(self, text='Сохранить')
        save_btn.Cmd(lambda e: self.save_settings())
        save_btn.pack(side=tkinter.LEFT, padx=10)

        cancel_btn = MyButton(self, text='Отмена')
        cancel_btn.Cmd(lambda e: self.winfo_toplevel().destroy())
        cancel_btn.pack(side=tkinter.LEFT)


    def save_settings(self):
        """
        Get text from all text fields in advanced settings and save to
        cfg.json
        """
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)

        new_values = [i.get() for i in Globals.inserts]
        for key, ins in zip(data, new_values):
            data[key] = ins

        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(data, file, indent=4)

        Globals.inserts = []
        self.winfo_toplevel().destroy()


class General(MyFrame):
    """
    Tkinter frame with general app settings.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master, padx=15)
        Globals.gen_frame = self

        title = MyLabel(self, text='Основные', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        txt1 = (
            'При запуске программа сканирует и обновляет фото'
            f'\nвсех коллекций за последние {cfg.FILE_AGE} дней.'
            '\nНажмите "Обновить", чтобы повторно запустить сканирование.')

        descr_updater = MyLabel(self)
        descr_updater.configure(
            text=txt1, justify=tkinter.LEFT, wraplength=350)
        descr_updater.pack(pady=(0, 10), anchor=tkinter.W)

        img_path = os.path.join(os.path.dirname(__file__), 'upd.png')
        img_src = Image.open(img_path)
        img_copy= img_src.copy()
        img_tk = ImageTk.PhotoImage(img_copy)

        img_lbl = MyLabel(self)
        img_lbl.configure(image=img_tk)
        img_lbl.pack()
        img_lbl.image_names = img_tk

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=20, fill=tkinter.X)

        txt2 = (
            'Нажмите "Полное сканирование", чтобы обновить'
            '\nфотографии всех коллекций за все время c 2018 года.')
        descr_scan = MyLabel(self)
        descr_scan.configure(
            text=txt2, justify=tkinter.LEFT, wraplength=350)
        descr_scan.pack(pady=(0, 10), anchor=tkinter.W)

        scan_btn = MyButton(self, text='Полное сканирование')
        scan_btn.Cmd(lambda e: self.full_scan())
        scan_btn.pack(anchor='center')

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=(25, 20), fill=tkinter.X)

        author_txt = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.')

        author_lbl = MyLabel(self)
        author_lbl.configure(
            text=author_txt, justify=tkinter.LEFT)
        author_lbl.pack(anchor=tkinter.W)

    def full_scan(self):
        """
        Reload app and run Utils Scaner with full scan method.
        """
        Dbase.conn.execute(sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='full'))
        os.execv(sys.executable, ['python'] + sys.argv)


class Expert(tkmacosx.SFrame):
    """
    Tkinter frame with advanced app settings.
    """
    def __init__(self, master):
        tkmacosx.SFrame.__init__(self, master, padx=15)
        self.configure(bg=cfg.BGCOLOR, scrollbarwidth=7)
        self.configure(avoidmousewheel=(self))
        Globals.adv_frame = self

        title = MyLabel(self, text='Эксперт', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)

        descr_list = []

        for _, value in data.items():
            desrc_input = MyLabel(self, justify=tkinter.LEFT, wraplength=340)
            desrc_input.pack(anchor=tkinter.W, pady=(0, 10))
            descr_list.append(desrc_input)

            text_input = tkinter.Entry(self, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
                insertbackground=cfg.FONTCOLOR, selectbackground=cfg.BGPRESSED,
                highlightthickness=5, highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON, bd=0, justify='center', width=35)

            text_input.insert(0, value)
            text_input.pack(pady=(0, 10))
            Globals.inserts.append(text_input)

            frame_btns = MyFrame(self)
            frame_btns.pack()

            btn_copy = MyButton(frame_btns, text='Копировать')
            btn_copy.configure(height=1, width=9)
            btn_copy.Cmd(
                lambda e, x=text_input, y=btn_copy: self.copy_input(x, y))
            btn_copy.pack(side=tkinter.LEFT, padx=(0, 10))

            btn_paste = MyButton(frame_btns, text='Вставить')
            btn_paste.configure(height=1, width=9)
            btn_paste.Cmd(
                lambda e, x=text_input, y=btn_paste: self.paste_input(x, y))
            btn_paste.pack(side=tkinter.RIGHT, padx=(0, 10))

            sep = Separator(self, orient='horizontal')
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        for descr_input, descr in zip(descr_list, descriptions):
            descr_input['text']=descr

        restore_btn = MyButton(self, text='По умолчанию')
        restore_btn.configure(height=1, width=12)
        restore_btn.Cmd(lambda e, x=restore_btn: self.restore(x))
        restore_btn.pack(pady=(0, 15))

    def restore(self, btn):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.Press()
        data = cfg.defaults
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(data, file, indent=4)

        for item, ins in zip(data.values(), Globals.inserts):
            ins.delete(0, 'end')
            ins.insert(0, item)

    def copy_input(self, ins, btn):
        """
        Gets text from current text input field and copy to clipboard.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.Press()
        my_copy(ins.get())

    def paste_input(self, ins, btn):
        """
        Gets text from clipboard and paste in text input field.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.Press()
        ins.delete(0, 'end')
        ins.insert(0, my_paste())
