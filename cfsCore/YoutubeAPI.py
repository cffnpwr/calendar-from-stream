import json
import re
import requests
from googleapiclient.discovery import build


class YoutubeAPI:

    def __init__(self, apiKey):
        self.youtube = build('youtube', 'v3', developerKey=apiKey)

    def getStreamDetailsFromURL(self, url):
        strmList = []

        cid = self.getChannelIdFromURL(url)

        if cid:
            ftrStrmList = self.getFutureStreamListFromChannel(cid)

            for strm in ftrStrmList:
                strmDetails = self.getStreamDetailsFromVideoID(strm)

                if strmDetails:
                    strmList.append(strmDetails)

        return strmList

    def getChannelIdFromURL(self, url):
        channelIdPattern = '(https?://)?(www.)?youtube.com/channel/UC[\w-]{22}/?'
        customURLPattern = '(https?://)?(www.)?youtube.com/(c/)?[\w]/?'
        usernamePattern = '(https?://)?(www.)?youtube.com/user/[\w]/?'

        if re.match(channelIdPattern, url):
            cid = re.search('UC[\w-]{22}', url).group()
            if self.youtube.channels().list(part='id', id=cid).execute()['pageInfo']['totalResults'] != 0:
                return cid
            return None

        elif re.match(customURLPattern, url) or re.match(usernamePattern, url):
            HTMLRes = requests.get(url).text
            cidRes = re.search(channelIdPattern, HTMLRes)
            if cidRes:
                return re.search('UC[\w-]{22}', cidRes.group()).group()

        return None

    def getFutureStreamListFromChannel(self, channelId):
        req = self.youtube.search().list(
            part='id',
            channelId=channelId,
            eventType='upcoming',
            type='video',
            maxResults=50,
            order='date'
        )
        rslt = req.execute()
        resultCnt = rslt['pageInfo']['totalResults']

        if resultCnt == 0:
            return None

        else:
            strmList = []
            for i in range(resultCnt):
                strmList.append(rslt['items'][i]['id']['videoId'])

            return strmList

    def getStreamDetailsFromVideoID(self, videoId):
        req = self.youtube.videos().list(
            part='snippet, liveStreamingDetails',
            id=videoId
        )
        rslt = req.execute()
        resultCnt = rslt['pageInfo']['totalResults']
        strmStat = rslt['items'][0]['snippet']['liveBroadcastContent']

        if resultCnt == 0 or strmStat != 'upcoming':
            return None

        else:
            strmDetails = {
                'who': rslt['items'][0]['snippet']['channelTitle'],
                'title': rslt['items'][0]['snippet']['title'],
                'url': 'https://www.youtube.com/watch?v=' + videoId,
                'startTime': convertTimeZone(convertISO8601ToYMDhmsZDic(rslt['items'][0]['liveStreamingDetails']['scheduledStartTime']), '+9')
            }

            return strmDetails


def convertISO8601ToYMDhmsZDic(date):
    ymd = date.split('-')
    dhm = ymd[2].split('T')
    hms = dhm[1].split(':')

    rsltDate = {
        'Y': int(ymd[0]),
        'M': int(ymd[1]),
        'D': int(dhm[0]),
        'h': int(hms[0]),
        'm': int(hms[1]),
        's': int(hms[2][0:2]),
        'Z': hms[2][2:]
    }

    return rsltDate


def convertTimeZone(YMDhmsZDic, dstTZ):
    tz = int(dstTZ[1:]) if dstTZ[0:1] == '+' else int(dstTZ)

    if YMDhmsZDic['Z'] == 'Z':
        nowTz = 0

    elif YMDhmsZDic['Z'][0:1] == '+':
        nowTz = int(YMDhmsZDic[1:3])

    else:
        nowTz = int(YMDhmsZDic[0:3])

    diff = tz - nowTz
    rsltDate = YMDhmsZDic

    rsltDate['h'] += diff
    if rsltDate['h'] < 0:
        rsltDate['D'] -= 1
        rsltDate['h'] += 24

    elif rsltDate['h'] > 24:
        rsltDate['D'] += 1
        rsltDate['h'] -= 24

    if rsltDate['D'] < 0:
        rsltDate['M'] -= 1

        if rsltDate['M'] == 2:
            rsltDate['D'] += 28

        elif rsltDate['M'] == 4 or rsltDate['M'] == 6 or rsltDate['M'] == 9 or rsltDate['M'] == 11:
            rsltDate['D'] += 30

        else:
            rsltDate['D'] += 31

    elif rsltDate['D'] > 28:
        rsltDate['M'] -= 1

        if rsltDate['M'] == 2:
            rsltDate['D'] -= 28

        elif (rsltDate['M'] == 4 or rsltDate['M'] == 6 or rsltDate['M'] == 9 or rsltDate['M'] == 11) and rsltDate['D'] > 30:
            rsltDate['D'] -= 30

        elif rsltDate['D'] > 31:
            rsltDate['D'] -= 31

        else:
            rsltDate['M'] += 1

    if rsltDate['M'] < 0:
        rsltDate['Y'] -= 1
        rsltDate['M'] += 12

    elif rsltDate['M'] > 12:
        rsltDate['Y'] += 1
        rsltDate['M'] -= 12

    return rsltDate
