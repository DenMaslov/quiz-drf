from quiz.celery import app
from .models import Testrun, Test
import datetime

import csv


@app.task
def update_csv_file():
    filename = 'report.csv'
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    test_sessions = Testrun.objects.filter(finished_at__gt=yesterday)
    tests = Test.objects.all()
    write_data_to_csv(filename, test_sessions, tests)


def write_data_to_csv(filename, test_sessions, tests):

    title_row = ['TEST', 'PASSED TODAY']
    stat_row = ['Completed', 'Incompleted', 'Completed, %', 'Incompleted, %']

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')

        writer.writerow(['Report updated:', str(datetime.date.today())])

        writer.writerow(stat_row)
        all_sessions = len(test_sessions)
        not_completed = len(test_sessions.filter(is_completed=False))
        completed = all_sessions - not_completed
        writer.writerow([str(completed),
                         str(not_completed),
                         str(round((completed / all_sessions), 4) * 100) + '%',
                         str(round((not_completed / all_sessions), 4) * 100) + '%',
                         ])

        writer.writerow(title_row)
        for test in tests:
            amount = len(test_sessions.filter(test=test))
            writer.writerow([test.title, str(amount), ])
