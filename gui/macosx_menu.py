import tkinter

import cfg
from utils import place_center

from .widgets import CLabel, CWindow, CloseBtn
from . import Settings


class BarMenu(tkinter.Menu):
    """
    Mac osx bar menu.
    """
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        tkinter.Menu.__init__(self, menubar)
        menubar.add_cascade(label="Меню", menu=self)
        self.add_command(
            label='Настройки', command=Settings)
        self.add_command(label="О программе", command=self.about_widget)
        self.add_separator()
        self.add_command(label="Выход", command=cfg.ROOT.destroy)
        cfg.ROOT.createcommand(
            'tkAboutDialog',
            lambda: cfg.ROOT.tk.call('tk::mac::standardAboutPanel'))
        cfg.ROOT.configure(menu=menubar)

    def about_widget(self):
        win = CWindow()
        made = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\n\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            '\n\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            )
        author = CLabel(win, text=made)
        author.pack(pady=(0, 10))
        close_btn = CloseBtn(win, text='Закрыть')
        close_btn.pack()

        cfg.ROOT.update_idletasks()
        place_center(win)
        win.deiconify()
        win.grab_set()
