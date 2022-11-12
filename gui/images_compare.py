import subprocess
import tkinter

import cfg
from utils import MyButton, MyFrame, MyLabel, my_copy, place_center

vars = {
    'img1': 'from tkinter top level: image, text, image src',
    'img2': 'from tkinter top level: image, text, image src',
    'curr_img': 'img1 or img2',
    'img_frame': 'tkinter label with image',
    'img_info': 'tkinter label with text',
    }


def on_closing(obj: tkinter.Toplevel):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """

    prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
    [i.destroy() for i in prevs]
    obj.destroy()
    cfg.COMPARE = False


class ImagesCompare(tkinter.Toplevel):
    """
    A new tkinter window containing two images and
    a button with an image switch.
    You can click the toggle button to see the difference between similar
    images
    """
    def __init__(self):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.title('Сравнение')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Command-q>', lambda e: quit())
        self.bind('<Escape>', lambda e: on_closing(self))

        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')
        cfg.ROOT.update_idletasks()

        prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]

        img1_info = list(prevs[0].children.values())
        img2_info = list(prevs[1].children.values())

        vars['img1'] = [
            img1_info[1]['image'],
            img1_info[3].children['!imginfo']['text'],
            img1_info[0]['text']
            ]

        vars['img2'] = [
            img2_info[1]['image'],
            img2_info[3].children['!imginfo']['text'],
            img2_info[0]['text']
            ]

        vars['curr_img'] = vars['img1']

        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True, pady=(0, 15))
        ImgButtons(self).pack(pady=(0, 15))
        ImgInfo(self).pack(pady=(0, 15), anchor=tkinter.CENTER)
        CloseBtn(self).pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self['image'] = vars['curr_img'][0]
        vars['img_frame'] = self

        self.update_idletasks()
        w = self.winfo_width()
        self.configure(width=w, height=w)


class ImgButtons(MyFrame):
    """
    Tkinter frame with buttons:
    * copy image name
    * open image folder
    * switch to second image
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = MyButton(self, text='Папка с фото')
        open_btn.configure(height=1, width=b_wight)
        open_btn.cmd(lambda e: self.open_folder(open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        toogle = MyButton(self, text='Переключить')
        toogle.configure(height=1, width=b_wight)
        toogle.cmd(lambda e: self.switch_image(toogle))
        toogle.pack(side=tkinter.LEFT, padx=(0, 0))

    def copy_name(self, btn: MyButton):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        get_name = vars['curr_img'][2].split('/')[-1].split('.')[0]
        my_copy(get_name)

    def open_folder(self, btn: MyButton):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(vars['curr_img'][2].split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])

    def switch_image(self, btn: MyButton):
        """
        Switches between two images from cfg.IMAGES_COMPARE set.
        """
        btn.press()

        for i in [vars['img1'], vars['img2']]:
            if vars['curr_img'] != i:
                vars['curr_img'] = i

                vars['img_frame']['image'] = vars['curr_img'][0]
                vars['img_info']['text'] = vars['curr_img'][1]

                return

class ImgInfo(MyLabel):
    """
    Creates tkinter frame with image info.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(
            self, master, anchor=tkinter.W, justify=tkinter.LEFT,
            text=vars['curr_img'][1], width=43)
        vars['img_info'] = self


class CloseBtn(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))
