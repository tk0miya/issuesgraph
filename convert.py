#!/usr/bin/env python

import io
import sys
import calendar
import pickle
from datetime import datetime, timedelta
from collections import namedtuple

from fetch import Issue  # NOQA


MIGRATED_TO_GITHUB = datetime(2015, 1, 2)


Period = namedtuple('Period',
                    ['name', 'begin', 'end'])


def next_month(d):
    max_day = calendar.monthrange(d.year, d.month)[1]
    return datetime(d.year, d.month, max_day) + timedelta(days=1)


def get_first_month():
    return MIGRATED_TO_GITHUB - timedelta(days=MIGRATED_TO_GITHUB.day - 1)


def get_month_periods():
    date = get_first_month()
    today = datetime.now()
    while date < today:
        period = Period(date.strftime('%Y/%m'),
                        date, next_month(date))
        yield period
        date = period.end


def get_first_week():
    weekday = MIGRATED_TO_GITHUB.weekday()
    return MIGRATED_TO_GITHUB - timedelta(days=weekday)


def get_week_periods():
    date = get_first_week()
    today = datetime.now()
    while date < today:
        period = Period(date.strftime('%Y-%m-%d'),
                        date, date + timedelta(weeks=1))
        yield period
        date = period.end


def parse_iso8601(datestring):
    if datestring:
        return datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
    else:
        return None


def main(args):
    with open('issues.dat', 'rb') as f:
        issues = pickle.load(f)

    summary = {}
    periods = list(get_month_periods())
    for period in periods:
        summary.setdefault(period, dict(opened_issues=0, closed_issues=0,
                                        opened_pr=0, closed_pr=0, total=0))

    for issue in issues:
        created_at = parse_iso8601(issue.created_at)
        closed_at = parse_iso8601(issue.closed_at)

        for period in periods:
            if period.end < created_at:  # not created yet
                pass
            else:
                summary[period]['total'] += 1
                if closed_at and closed_at < period.end:
                    if issue.type == 'issue':
                        summary[period]['closed_issues'] += 1
                    else:
                        summary[period]['closed_pr'] += 1
                else:
                    if issue.type == 'issue':
                        summary[period]['opened_issues'] += 1
                    else:
                        summary[period]['opened_pr'] += 1

    with io.open('export.csv', 'w') as f:
        columns = [
            "month",
            "opened_issues", "opened_pr", "closed_issues", "closed_pr",
            "total", "", "increase/mo", "close/mo"
        ]
        f.write(','.join(columns) + "\n")
        for i, period in enumerate(periods):
            result = summary[period]
            data = (period.name,
                    result['opened_issues'], result['opened_pr'],
                    result['closed_issues'], result['closed_pr'],
                    result['total'])
            f.write(u"%s,%s,%s,%s,%s,%s,," % data)
            if i == 0:
                f.write(u"-,-\n")
            else:
                prev = i + 1
                curr = i + 2
                f.write(u"=F%d-F%d," % (curr, prev))
                f.write(u"=SUM(D%d:E%d)-SUM(D%d:E%d)" %
                        (curr, curr, prev, prev))
                f.write(u"\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
