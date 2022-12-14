import os
import shutil
import tkinter

from utils import write_cfg, read_cfg

# app info
APP_NAME = 'MiuzPhoto'
APP_VER = '3.2.4'

KEY = 'QaovKbF1YpKCM9e-HE2wvn30lIqCbeYTUcONcdLpV18='
CFG_DIR = os.path.join(
    os.path.expanduser('~'), f'Library/Application Support/{APP_NAME}')

# database info
DB_VER = '1.1'
DB_NAME = f'db {DB_VER}.db'

# gui settings
BGFONT = "#E2E2E2"
BGCOLOR = "#1A1A1A"
BGBUTTON = "#2C2C2C"
BGPRESSED = '#395432'
BGSELECTED = '#4E4769'
THUMB_SIZE = 150

# flags
FLAG = False
COMPARE = False

# gui objects for global access
ROOT = tkinter.Tk()
ROOT.withdraw()
GALLERY = object
ST_BAR = object

default_vars = {
        'PHOTO_DIR': '/Volumes/Shares/Marketing/Photo',
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',
        'RT_FOLDER': 'Retouch',
        'FILE_AGE': 60,
        'GEOMETRY': [700, 500, 0, 0],
        'WIN_GEOMETRY': [700, 500],
        'CURR_COLL': 'last',
        'TYPE_SCAN': '',
        'MINIMIZE': 1
        }

old_path = os.path.join(os.path.split(CFG_DIR)[0], 'Miuz Gallery')
if os.path.exists(old_path):
    shutil.rmtree(old_path)

if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if not os.path.exists(os.path.join(CFG_DIR, DB_NAME)):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'db.db'),
        os.path.join(CFG_DIR, DB_NAME))

for file in os.listdir(CFG_DIR):
    if file.endswith('.db') and file != DB_NAME:
        os.remove(os.path.join(CFG_DIR, file))

if os.path.exists(os.path.join(CFG_DIR, 'cfg')):
    config = read_cfg(os.path.join(CFG_DIR, 'cfg'))
else:
    config = default_vars
    write_cfg(config)

part1 = {k:v for k, v in config.items() if k in default_vars.keys()}
part2 = {k:v for k, v in default_vars.items() if k not in config.keys()}
new_config = {**part1, **part2}
write_cfg(new_config) if new_config.keys() != config.keys() else False
config = new_config if new_config.keys() != config.keys() else config
