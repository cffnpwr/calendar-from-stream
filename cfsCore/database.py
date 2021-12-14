import psycopg2
import psycopg2.extras
import html


class Database:

    def __init__(self, host, port, name, user, passwd):
        self.dbCon = psycopg2.connect(
            host=host, port=port, dbname=name, user=user, password=passwd)

    def __del__(self):
        self.dbCon.close()

    def getAllRecords(self, table):
        with self.dbCon.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('select * from ' + html.escape(table))
            rslt = cur.fetchall()

        dicRslt = []
        for row in rslt:
            dicRslt.append(dict(row))

        return dicRslt

    def getAllRecordsWithColumns(self, table, columns):
        cols = ''

        for col in columns:
            cols += ('"' + html.escape(col) + '", ')

        cols = cols[:-2]

        sql = 'select ' + cols + ' from ' + html.escape(table)

        with self.dbCon.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            rslt = cur.fetchall()

        dicRslt = []
        for row in rslt:
            dicRslt.append(dict(row))

        return dicRslt
