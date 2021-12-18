import subprocess
import schedule
import time


def execCfsCore():
    try:
        res = subprocess.check_output(['python', 'main.py'])
        print(res.decode(encoding='utf-8'))

    except Exception as e:
        print(e)


schedule.every().hours.do(execCfsCore)

while True:
    schedule.run_pending()
    time.sleep(1)
