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
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


def main():
    print(datetime.datetime.now(JST).strftime(
        '%Y-%m-%d %H:%M:%S :: ') + 'start!!')

    tokenList = getAccessTokenList()
    streamDetailsList = getStreamDetailList()

    initCalendar()

    for userId, token in tokenList.items():
        try:
            EinY = streamDetailsList[userId]

            calendarId = getCalendarIdFromDB(userId)

            clndr = CalendarAPI(CLIENT_ID, CLIENT_SECRET, token)
            EinC = clndr.getEvents(calendarId)

            for i, ec in enumerate(EinC):
                if datetime.datetime.fromisoformat(ec['start']['dateTime']).astimezone(JST) < datetime.datetime.now(JST):
                    del EinC[i]

            for ey in EinY:
                isExist = False
                for i, ec in enumerate(EinC):
                    if 'location' in ec:
                        if ey['url'] == ec['location']:
                            dt = ey['startTime']
                            tz = datetime.timezone.utc if dt['Z'] == 'Z' else datetime.timezone(
                                datetime.timedelta(hours=dt['Z']))
                            eyStartTime = datetime.datetime(
                                dt['Y'], dt['M'], dt['D'], dt['h'], dt['m'], dt['s'], tzinfo=tz).astimezone(JST)
                            ecStartTime = datetime.datetime.fromisoformat(
                                ec['start']['dateTime']).astimezone(JST)
                            if ey['title'] != ec['summary'] or eyStartTime != ecStartTime or ey['who'] != ec['description']:
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
                                print('[update] ' + ey['title'])

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
                    print('[insert] ' + ey['title'])

            #   すべてが終わったら
            #   残ったEinCを予定から削除
            for ec in EinC:
                clndr.deleteEvent(calendarId, ec['id'])
                print('[delete] ' + ec['summary'])

            del clndr

        except:
            pass

    print(datetime.datetime.now(JST).strftime(
        '%Y-%m-%d %H:%M:%S :: ') + 'finished!!')


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
                try:
                    strmDetails += yt.getStreamDetailsFromURL(url)

                except Exception as e:
                    print('ERROR!!')
                    print(e.args)
                    print('stopped!!')
                    break

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

            if ('id' in newTokenDic) and ('accessToken' in newTokenDic) and ('exp' in newTokenDic):
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
                    newAccessToken = ''

            else:
                newAccessToken = ''

            accessToken = newAccessToken

        accessTokenList[record['id']] = accessToken

    del db

    return accessTokenList


def initCalendar():
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    users = db.getAllRecordsWithColumns(
        DB_TABLE, ['id', 'accessToken', 'calendarId'])

    for user in users:
        clndr = CalendarAPI(CLIENT_ID, CLIENT_SECRET, user['accessToken'])
        if not ('calendarId' in user) or not (clndr.getCalendar(user['calendarId'])):
            try:
                clndrId = clndr.makeNewCalendar(
                    '配信予定', description='create by Calendar from Stream Service')
                del clndr

                db.updateRecordWithColumns(DB_TABLE, {'calendarId': clndrId}, {
                    'id': user['id']})

            except:
                pass


def getCalendarIdFromDB(userId):
    db = Database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    cId = db.getRecordWithColumns(
        DB_TABLE, ['calendarId'], {'id': userId})

    return cId[0]['calendarId']


if __name__ == '__main__':
    main()
