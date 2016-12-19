#!/usr/bin/env python

import io
import sys
import calendar
import cPickle as pickle
from datetime import datetime, timedelta
from collections import namedtuple


MIGRATED_TO_GITHUB = datetime(2015, 1, 2)


Issue = namedtuple('Issue',
                   ['number', 'url', 'state', 'created_at', 'closed_at'])
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
        summary.setdefault(period, dict(opened=0, closed=0))

    for issue in issues:
        created_at = parse_iso8601(issue.created_at)
        closed_at = parse_iso8601(issue.closed_at)

        for period in periods:
            if period.end < created_at:  # not created yet
                pass
            elif closed_at and closed_at < period.end:
                summary[period]['closed'] += 1
            else:
                summary[period]['opened'] += 1

    with io.open('export.csv', 'w') as f:
        f.write(u"month,opened,closed,total,,increase/month,close/month\n")
        for i, period in enumerate(periods):
            result = summary[period]
            if i == 0:
                f.write(u"%s,%s,%s,%s,,-,-\n" % (
                    period.name, result['opened'], result['closed'],
                    result['opened'] + result['closed']
                ))
            else:
                f.write(u"%s,%s,%s,%s,,=D%d-D%d,=C%d-C%d\n" % (
                    period.name, result['opened'], result['closed'],
                    result['opened'] + result['closed'],
                    i + 2, i + 1, i + 2, i + 1
                ))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
