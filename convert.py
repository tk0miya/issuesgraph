#!/usr/bin/env python

import io
import sys
import calendar
import cPickle as pickle
from datetime import date, datetime, timedelta
from collections import namedtuple


MIGRATED_TO_GITHUB = datetime(2015, 1, 2)


Issue = namedtuple('Issue',
                   ['number', 'url', 'state', 'created_at', 'closed_at'])


def next_month(d):
    max_day = calendar.monthrange(d.year, d.month)[1]
    return datetime(d.year, d.month, max_day) + timedelta(days=1)


def get_calendar():
    d = next_month(MIGRATED_TO_GITHUB)
    while d < next_month(datetime.now()):
        yield d
        d = next_month(d)


def parse_iso8601(datestring):
    if datestring:
        return datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
    else:
        return None


def main(args):
    with open('issues.dat', 'rb') as f:
        issues = pickle.load(f)

    summary = {}
    months = list(get_calendar())
    for month in months:
        summary.setdefault(month, dict(opened=0, closed=0))

    for issue in issues:
        created_at = parse_iso8601(issue.created_at)
        closed_at = parse_iso8601(issue.closed_at)

        for month in months:
            if month < created_at:  # not created yet
                pass
            elif closed_at and closed_at < month:
                summary[month]['closed'] += 1
            else:
                summary[month]['opened'] += 1

    with io.open('export.csv', 'w') as f:
        f.write(u"month,opened,closed,total\n")
        for month in months:
            result = summary[month]
            f.write(u"%s,%s,%s,%s\n" % (
                month, result['opened'], result['closed'],
                result['opened'] + result['closed']
            ))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
