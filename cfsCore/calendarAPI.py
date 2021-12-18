import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class CalendarAPI:
    def __init__(self, clientId, clientSecret, accessToken):
        cred = Credentials(
            accessToken,
            client_id=clientId,
            client_secret=clientSecret,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        self.clndr = build('calendar', 'v3', credentials=cred)

    def __del__(self):
        self.clndr.close()

    def makeNewCalendar(self, summary, description='', timeZone='Asia/Tokyo'):
        calendar = {
            'summary': summary,
            'description': description,
            'timeZone': timeZone
        }

        res = self.clndr.calendars().insert(body=calendar).execute()

        if 'error' in res:
            return None

        return res['id']

    def getCalendar(self, calendarId):
        try:
            rslt = self.clndr.calendars().get(calendarId=calendarId).execute()

            return rslt

        except:
            return None

    def getEvents(self, calendarId, timeMin=datetime.datetime.now(datetime.timezone.utc).isoformat(), orderBy='startTime'):
        rslts = self.clndr.events().list(
            calendarId=calendarId,
            timeMin=timeMin,
            singleEvents=True,
            orderBy=orderBy
        ).execute()
        events = rslts.get('items', [])

        return events

    def updateEvent(self, calendarId, eventId, body):
        self.clndr.events().patch(
            calendarId=calendarId,
            eventId=eventId,
            body=body
        ).execute()

    def deleteEvent(self, calendarId, eventId):
        self.clndr.events().delete(
            calendarId=calendarId,
            eventId=eventId
        ).execute()

    def insertEvent(self, calendarId, body, start='', end=''):
        body['start'] = start
        body['end'] = end
        self.clndr.events().insert(
            calendarId=calendarId,
            body=body
        ).execute()
