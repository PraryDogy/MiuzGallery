import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils import Main as Utils


def Scan():
    '''
    Run Utils files scan & database update.
    '''
    cfg.FLAG = True
    selectType = sqlalchemy.select(Config.value).where(
        Config.name=='typeScan')
    typeScan = dBase.conn.execute(selectType).first()[0]
    
    Utils.CollsUpd().CollsUpd()

    if typeScan == 'full':

        updateType = sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='')
        dBase.conn.execute(updateType)

        Utils.RtUpd().RtUpd()
        return

    Utils.RtUpd().RtAgedUpd()


def Skip(topLevel):
    '''
    Destroys tkinter topLevel window and set cfg.FLAF to False.
    '''
    topLevel.withdraw()
    topLevel.destroy()
    cfg.FLAG = False
    print('skip done')