#!/usr/bin/env python3

import csv
import sys
import datetime
import zoneinfo
import argparse

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
    return parser.parse_args()


def csv_output(data, tz=datetime.timezone.utc):
    writer = csv.writer(sys.stdout)
    writer.writerow(["Date and time", "EUR/MWh"])
    writer.writerows((d.astimezone(tz).replace(tzinfo=None), p) for d, p in data)


def main():
    args = parse_options()
    doc = download_xml(args.start, args.end, market=args.market)
    data = parse_xml_doc(doc)
    csv_output(data, args.tz)


if __name__ == '__main__':
    main()
