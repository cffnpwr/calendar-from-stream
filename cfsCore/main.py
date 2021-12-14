from decouple import config

from YoutubeAPI import YoutubeAPI
from database import Database


YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
DB_HOST = 'db'
DB_PORT = '5432'
DB_NAME = 'cfs'
DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_TABLE = 'user_user'

'''
DBから全取得 <- ok
Youtube API で配信予定取得 <- ok
既存の予定とURLで照合 <- イマココ
時間変更、新規追加、未来の予定が消えてたら削除
'''


def main():
    if __name__ != '__main__':
        quit()

    print(getStreamDetailList())


def getStreamDetailList():
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    urlLists = db.getAllRecordsWithColumns(DB_TABLE, ['id', 'urlList'])

    yt = YoutubeAPI(YOUTUBE_API_KEY)

    strmDetailsList = {}

    for urlList in urlLists:
        strmDetails = []

        for urls in urlList['urlList'].values():
            for url in urls:
                strmDetails += yt.getStreamDetailsFromURL(url)

        strmDetailsList[urlList['id']] = strmDetails

    del db

    return strmDetailsList


main()
