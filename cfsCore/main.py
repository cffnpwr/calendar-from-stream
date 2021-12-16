import datetime
from decouple import config

import googleAPIs
from youtubeAPI import YoutubeAPI
from database import Database


YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
CLIENT_ID = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
CLIENT_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
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

    print(getAccessTokenList())


def getStreamDetailList():
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    urlLists = db.getAllRecordsWithColumns(DB_TABLE, ['id', 'urlList'])

    del db

    yt = YoutubeAPI(YOUTUBE_API_KEY)

    strmDetailsList = {}

    for urlList in urlLists:
        strmDetails = []

        for urls in urlList['urlList'].values():
            for url in urls:
                strmDetails += yt.getStreamDetailsFromURL(url)

        strmDetailsList[urlList['id']] = strmDetails

    return strmDetailsList


def getAccessTokenList():
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    records = db.getAllRecordsWithColumns(
        DB_TABLE, ['id', 'accessToken', 'refreshToken', 'expiryDate'])

    accessTokenList = {}

    for record in records:
        accessToken = record['accessToken']

        if record['expiryDate'] < datetime.datetime.now(datetime.timezone.utc):
            newTokenDic = googleAPIs.getNewAccessToken(
                CLIENT_ID, CLIENT_SECRET, record['refreshToken'])

            newExpiryDate = datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(seconds=newTokenDic['exp'])
            if newTokenDic['id'] == record['id'] and newExpiryDate > datetime.datetime.now(datetime.timezone.utc):
                newAccessToken = newTokenDic['accessToken']

                values = {
                    'accessToken': newAccessToken,
                    'expiryDate': newExpiryDate
                }
                cond = {
                    'id': record['id']
                }

                db.updateRecordWithColumns(DB_TABLE, values, cond)

            else:
                newAccessToken = None

            accessToken = newAccessToken

        accessTokenList[record['id']] = accessToken

    del db

    return accessTokenList


main()
