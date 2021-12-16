import schedule
import time
import datetime
from decouple import config

import googleAPIs
from youtubeAPI import YoutubeAPI
from calendarAPI import CalendarAPI
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
    print('start!!')

    tokenList = getAccessTokenList()
    streamDetailsList = getStreamDetailList()

    initCalendar()

    for userId, token in tokenList.items():
        EinY = streamDetailsList[userId]

        calendarId = getCalendarIdFromDB(userId)

        clndr = CalendarAPI(CLIENT_ID, CLIENT_SECRET, token)
        EinC = clndr.getEvents(calendarId)

        for ey in EinY:
            isExist = False
            for i, ec in enumerate(EinC):
                if 'location' in ec:
                    if ey['url'] == ec['location']:
                        dt = ey['startTime']
                        tz = datetime.timezone.utc if dt['Z'] == 'Z' else datetime.timezone(
                            datetime.timedelta(hours=dt['Z']))
                        eyStartTime = datetime.datetime(
                            dt['Y'], dt['M'], dt['D'], dt['h'], dt['m'], dt['s'], tzinfo=tz)
                        if ey['title'] != ec['summary'] or eyStartTime != ec['start']['dateTime'] or ey['who'] != ec['description']:
                            #   カレンダーの更新
                            body = {
                                'summary': ey['title'],
                                'description': ey['who'],
                                'start': {
                                    'dateTime': eyStartTime.isoformat()
                                },
                                'end': {
                                    'dateTime': (eyStartTime + datetime.timedelta(hours=1)).isoformat()
                                }
                            }
                            clndr.updateEvent(calendarId, ec['id'], body)

                        #   特定URLの予定が存在する
                        #   ここでEinCからecを削除する
                        del EinC[i]
                        isExist = True
                        break

                    #   URLが違うので次のecへ

            #   ecが存在したなら何もしない
            #   ecが存在しなかったら予定追加
            if not isExist:
                #   予定追加
                dt = ey['startTime']
                tz = datetime.timezone.utc if dt['Z'] == 'Z' else datetime.timezone(
                    datetime.timedelta(hours=dt['Z']))
                eyStartTime = datetime.datetime(
                    dt['Y'], dt['M'], dt['D'], dt['h'], dt['m'], dt['s'], tzinfo=tz)
                body = {
                    'summary': ey['title'],
                    'description': ey['who'],
                    'location': ey['url']
                }
                startTime = {'dateTime': eyStartTime.isoformat()}
                endTime = {'dateTime': (
                    eyStartTime + datetime.timedelta(hours=1)).isoformat()}
                clndr.insertEvent(calendarId, body, startTime, endTime)

        #   すべてが終わったら
        #   残ったEinCを予定から削除
        for ec in EinC:
            clndr.deleteEvent(calendarId, ec['id'])

        del clndr

    print('finished!!')


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


def initCalendar():
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    noClndrIds = db.getRecordWithColumns(
        DB_TABLE, ['id', 'accessToken'], {'calendarId': ''})

    for noClndrId in noClndrIds:
        clndr = CalendarAPI(CLIENT_ID, CLIENT_SECRET, noClndrId['accessToken'])
        clndrId = clndr.makeNewCalendar(
            '配信予定', description='create by Calendar from Stream Service')
        del clndr

        db.updateRecordWithColumns(DB_TABLE, {'calendarId': clndrId}, {
                                   'id': noClndrId['id']})


def getCalendarIdFromDB(userId):
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    cId = db.getRecordWithColumns(
        DB_TABLE, ['calendarId'], {'id': userId})

    return cId[0]['calendarId']


if __name__ == '__main__':
    schedule.every(10).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
