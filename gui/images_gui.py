"""
Gui menu and images grid.
"""

import os
import re
import subprocess
import tkinter
import traceback
from datetime import datetime

import cfg
import cv2
import numpy
import sqlalchemy
import tkmacosx
from database import Config, Dbase, Thumbs
from PIL import Image, ImageTk
from utils import MyButton, MyFrame, MyLabel

from .image_viewer import ImagePreview


def get_curr_coll():
    """
    Returns name of selected collection.
    Loads from Database > Config > currColl > value.
    """
    return Dbase.conn.execute(sqlalchemy.select(Config.value).where(
        Config.name=='currColl')).first()[0]


class Gallery(MyFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        MenuButtons(self).pack(
            pady=(0, 0), padx=(0, 15), side=tkinter.LEFT, fill=tkinter.Y)
        ImagesThumbs(self).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)


class MenuButtons(tkmacosx.SFrame):
    """
    Creates tkinter buttons with vertical pack.
    Buttons based on list of collections.
    List of collections based on Database > Thumbs.collection.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7, width=150)

        img_src = Image.open(
            os.path.join(os.path.dirname(__file__), 'logo.png'))

        img_tk= ImageTk.PhotoImage(img_src)

        img_lbl = MyLabel(self)
        img_lbl.configure(image=img_tk)
        img_lbl.pack(pady=(0, 0))
        img_lbl.image_names = img_tk

        company_name = MyLabel(
            self, text='Коллекции', font=('Arial', 18, 'bold'))
        company_name.pack(pady=(15, 20))

        __res = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)).fetchall()
        __colls_list = set(i[0] for i in __res)

        for_btns = []
        for coll_item in __colls_list:
            name_btn = coll_item.replace(
                re.search(r'(\d{0,30}\s){,1}', coll_item).group(),
                '')
            for_btns.append((name_btn[:13], coll_item))
        for_btns.sort()

        curr_coll = get_curr_coll()
        btns = []
        for name_btn, name_coll in for_btns:

            btn = MyButton(self, text=name_btn)
            btn.configure(height=1, width=12 ,pady=1)
            btn.pack(pady=(0, 10))
            btns.append(btn)

            if name_coll == curr_coll:
                btn.configure(bg=cfg.BGPRESSED)

            btn.cmd(lambda e, coll=name_coll, btn=btn, btns=btns:
                    self.__open_coll(coll, btn, btns))

        last_imgs = MyButton(self, text='Последние')
        last_imgs.configure(height=1, width=12)
        last_imgs.cmd(lambda e: self.__open_coll('last', last_imgs, btns))
        last_imgs.pack(pady=(0, 10))
        btns.append(last_imgs)

        if curr_coll == 'last':
            last_imgs.configure(bg=cfg.BGPRESSED)

    def __open_coll(self, coll, btn, btns):
        """
        Changes all buttons color to default and change color for
        pressed button.
        Updates database > config > currColl > value to collection from
        button.
        Runs GalleryReset.
        * param `coll`: str, real collection name from path to img
        * param `btn`: tkinter curren button object
        * param `btns`: list of created tkinter buttons
        """

        if btn['bg'] == cfg.BGPRESSED:
            coll_path = os.path.join(os.sep, cfg.config['COLL_FOLDER'], coll)
            subprocess.check_output(["/usr/bin/open", coll_path])
            return

        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON
        btn['bg'] = cfg.BGPRESSED

        Dbase.conn.execute(sqlalchemy.update(Config).where(
            Config.name=='currColl').values(value=coll))

        cfg.IMAGES_RESET()


class ImagesThumbs(tkmacosx.SFrame):
    """
    Creates images grid based on database thumbnails.
    Grid is labels with images created with pack method.
    Number of columns in each row based on Database > Config > clmns > value.
    * param `master`: tkmacosx scrollable frame.
    """
    def __init__(self, master):
        self.master = master
        cfg.IMAGES_RESET = self.reset

        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7)

        w = int(cfg.config["ROOT_SIZE"].split('x')[0])
        self.clmns = ((w)//158)-1

        curr_coll = get_curr_coll()

        title = MyLabel(
            self, text=curr_coll, font=('Arial', 45, 'bold'))
        title.pack(pady=(0, 15))

        if curr_coll == 'last':
            title.configure(text='Последние добавленные')
            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150, Thumbs.src, Thumbs.modified
                    ).order_by(
                    -Thumbs.modified).limit(120)).fetchall()
        else:
            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150, Thumbs.src, Thumbs.modified
                    ).where(
                    Thumbs.collection==curr_coll
                    ).order_by(
                        -Thumbs.modified)).fetchall()

        thumbs = self.load_thumbs(res)

        if len(thumbs) == 0:
            return

        for y in self.split_years(thumbs):

            year_label = MyLabel(
                self, text=y[-1][-1], font=('Arial', 35, 'bold'))
            year_label.pack(pady=(15, 15))

            self.pack_rows(y, self.clmns, self)

    def reset(self):
        """
        Destroys self.Run init again
        """
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        cfg.config['ROOT_SIZE'] = f'{w}x{h}'
        self.destroy()
        ImagesThumbs(self.master).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)

    def load_thumbs(self, all_images):
        """
        Loads thumbnails from database > thumbnails based on size from
        database > config > size > value.
        * returns: list turples: (img, src, modified)
        """

        thumbs = []
        for blob, src, mod in all_images:
            try:
                nparr = numpy.frombuffer(blob, numpy.byte)
                image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

                # convert cv2 color to rgb
                image_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

                # load numpy array image
                image = Image.fromarray(image_rgb)
                photo = ImageTk.PhotoImage(image)
                year = datetime.fromtimestamp(mod).year
                thumbs.append((photo, src, year))

            except Exception:
                print(traceback.format_exc())

        return thumbs

    def split_years(self, thumbs):
        """
        Splits a list into lists by year.
        * returns: list of lists
        * param `thumbs`: list tuples (imageTk, image src, image year modified)
        """
        years = set(year for _, _, year in thumbs)
        list_years = []

        for y in years:
            tmp = [(im, src, year) for im, src, year in thumbs if year == y]
            list_years.append(tmp)
        list_years.reverse()
        return list_years

    def pack_rows(self, thumbs, clmns, master):
        """
        Splits list of tuples by the number of lists.
        Each list is row with number of columns based on 'clmns'.

        In short we create images grid with a number columns from images list
        with tkinter pack method.
        Tkinter pack don't have 'new line' method and we need create
        tkinter frame for each row with images. For this we split big list
        into small lists, each of which is row with tkinter labels.

        * param `thumbs`: list tuples(imageTk, image src, image year)
        * param `clmns`: int from database > config > clmns > value
        * param `master`: tkinter frame
        """

        img_rows = [thumbs[x:x+clmns] for x in range(0, len(thumbs), clmns)]

        for row in img_rows:

            row_frame = MyFrame(master)
            row_frame.pack(fill=tkinter.Y, expand=True, anchor=tkinter.W)

            for image, src, _ in row:
                thumb = MyButton(row_frame, image=image, highlightthickness=1)
                thumb.configure(width=0, height=0, bg=cfg.BGCOLOR)
                thumb.image_names = image
                thumb.cmd(lambda e, src=src: ImagePreview(src))
                thumb.pack(side=tkinter.LEFT)
