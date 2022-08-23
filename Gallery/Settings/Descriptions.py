SMB_DIR = ('Путь к сетевому диску Miuz. По нему MiuzGallery проверяет '
            'доступность диска.')

SMB_CONN = ('Путь к сетевому диску для кнопки "Подключиться", когда '
            'сетевой диск недоступен')

PHOTO_DIR = ('Путь ко всем фотографиям Miuz.'
            '\nНапример: /Путь/к/сетевому/диску/Miuz/AllPhotos'
            '\n\nПодразумевается, что '
            'внутри этой папки будут папки с годами: 2018, 2019...2022 и т.д.'
            '\nНапример: /Путь/к/сетевому/диску/Miuz/AllPhotos/2022')

COLL_FOLDER = ('Название папки, внутри которой находятся '
               'папки с коллекциями. Папку с коллекциями MiuzGallery '
               'ищет в папке со всеми фотографиями Miuz, '
               'указанную по пути выше.')

RT_FOLDER = ('Название папки, внутри которой находятся '
             'отретушированные фотографии. '
             'MiuzGallery ищет все папки с данным '
             'названием в папке со всеми фотографиями Miuz.')

FILE_AGE = ('По умолчанию MiuzGallery ищет папки Retouch (см. выше) '
            'в папке со всеми фотографиями Miuz за последние 60 дней. '
            'Здесь можно указать другое количество дней.')


descriptions = [SMB_DIR, SMB_CONN, PHOTO_DIR, 
                COLL_FOLDER, RT_FOLDER, FILE_AGE]