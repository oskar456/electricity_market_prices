#!/usr/bin/env python3

import csv
import sys
import datetime
import zoneinfo
import argparse
import logging

logger = logging.getLogger(__name__)

from market_prices import download_xml, parse_xml_doc, datetime_parser


def parse_options():
    parser = argparse.ArgumentParser(
            description="Download and present hourly market prices "
                        "as CSV"
    )
    parser.add_argument("-s", "--start", help="start date",
                        metavar="YYYYMMDD", type=datetime_parser)
    parser.add_argument("-e", "--end", help="end date",
                        metavar="YYYYMMDD", type=datetime_parser)
    parser.add_argument("-t", "--tz", help="time zone",
                        metavar="ZONE", type=lambda tz:zoneinfo.ZoneInfo(tz),
                        default=datetime.timezone.utc)
    parser.add_argument("--market", help="market id",
                        default='10YNL----------L')
    parser.add_argument("--log-level", default=logging.INFO,
                        type=lambda x: getattr(logging, x),)
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    return args


def csv_output(data, tz=datetime.timezone.utc):
    writer = csv.writer(sys.stdout)
    writer.writerow(["Date and time", "EUR/MWh"])
    writer.writerows((d.astimezone(tz).replace(tzinfo=None), p) for d, p in data)


def repair_sequence(data):
    """
    Make sure that data contains all hours. If there's gap between data,
    replace it with repeated data for the previous hour.
    """
    hour = datetime.timedelta(hours=1)
    i = iter(data)
    try:
        old = next(i)
    except StopIteration:
        return

    for d in i:
        yield old
        td = d[0] - old[0]
        while td > hour:
            old = (old[0] + hour, old[1])
            td -= hour
            yield old
        old = d
    yield old


def main():
    args = parse_options()
    if args.start is None:
        td = datetime.date.today()
        args.start = datetime.datetime(td.year, td.month, td.day, tzinfo=args.tz)
    if args.end is None:
        args.end = datetime.timedelta(days=2) + args.start
    last_date = args.start
    data = []
    while args.end - last_date >= datetime.timedelta(days=1):
        doc = download_xml(last_date, args.end, market=args.market)
        d = list(parse_xml_doc(doc))
        logger.debug("Retrieving data from %s, retrieved %i items.",
                     last_date, len(d))
        if len(d) == 0 or d[-1] in data:
            break
        data.extend(d)
        last_date = data[-1][0] + datetime.timedelta(hours=1)
    data = repair_sequence(data)
    csv_output(data, args.tz)


if __name__ == '__main__':
    main()
