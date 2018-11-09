#!/usr/bin/env python3
# Nerius Ilmonas 2018

import requests
import datetime
import os
import sys
import math
from dateutil import parser
from xml.dom import minidom


def print_info(upto, show_all, username, password):

    if not username or not password:
        print('Usage: python3 timetable.py -u [USERNAME]* -p [PASSWORD]* (-n [LESSON INDEX] / -all)')

    global BASE_URL, NAMESPACE, APP_TOKEN
    BASE_URL = 'https://campusm.kcl.ac.uk//kcl_live/services/CampusMUniversityService/retrieveCalendar'
    NAMESPACE = 'http://campusm.gw.com/campusm'
    APP_TOKEN = 'YXBwbGljYXRpb25fc2VjX3VzZXI6ZjJnaDUzNDg='
    
    # Fetch and parse calender data
    calendar = fetch_calender(username, password)
    lectures = parse_xml(calendar)

    # Get data and print to screen
    for i in range(upto - 1 if not show_all else 0, upto if not show_all else len(lectures)):
        try:
            title = lectures[i].childNodes[0].childNodes[0].nodeValue
            desc = lectures[i].childNodes[1].childNodes[0].nodeValue
            start = parser.parse(lectures[i].childNodes[2].childNodes[0].nodeValue)
            end = parser.parse(lectures[i].childNodes[3].childNodes[0].nodeValue)
            if 'Prac' in title or 'SmG' in title or 'ClassTest' in title:
                teacher = 'None'
                location_code = lectures[i].childNodes[4].childNodes[0].nodeValue    
                location = lectures[i].childNodes[5].childNodes[0].nodeValue
            else:    
                teacher = lectures[i].childNodes[4].childNodes[0].nodeValue
                location_code = lectures[i].childNodes[5].childNodes[0].nodeValue
                location = lectures[i].childNodes[6].childNodes[0].nodeValue

            date = '{}/{}/{}'.format(start.strftime('%d'), start.strftime('%m'), start.strftime('%Y'))
            print('{}\n{}\nDate: {}\nTime: {} - {}\nTeacher(s): {}\nLocation Code: {}\nLocation: {}\n'.format(title, desc, date, format_date(start), format_date(end), teacher, location_code, location))
        except:
            print('You have {} lectures between today and tomorrow!'.format(len(lectures)))

def make_calendar_payload(username, password, start, end):

    # Create payload for fetching calender
    payload = '<retrieveCalendar xmlns=\"{}\">\n'.format(NAMESPACE)
    payload += '    <username>{}</username>\n'.format(username)
    payload += '    <password>{}</password>\n'.format(password)
    payload += '    <calType>course_timetable</calType>\n'
    payload += '    <start>{}</start>\n'.format(start.isoformat())
    payload += '    <end>{}</end>\n'.format(end.isoformat())
    payload += '</retrieveCalendar>'

    return payload


def fetch_calender(username, password):
    # Get calender for current day
    today = datetime.datetime.today()
    start = datetime.datetime(today.year, today.month, today.day, math.floor(today.hour), 0, 0, 0, today.tzinfo)
    end = datetime.datetime.today() + datetime.timedelta(days=1, hours=-start.hour + 24, minutes=-start.minute, seconds=-start.second, microseconds=-start.microsecond)

    # Create headers, payload and request
    _headers = {
        'Content-Type': 'application/xml',
        'Authorization': 'Basic ' + APP_TOKEN
    }
    payload = make_calendar_payload(username, password, start, end)
    response = requests.post(BASE_URL, data=payload.encode('utf-8'), headers=_headers)
    
    return response.text


def parse_xml(xml):
    # Parse the XML
    xmldoc = minidom.parseString(xml)
    lectures = xmldoc.getElementsByTagName('ns1:calitem')
    
    # Sort the lectures by date and return
    return sorted(lectures, key=lambda x: parser.parse(x.childNodes[2].childNodes[0].nodeValue))
    

def format_date(date):
    return '{}:{}'.format(date.strftime('%H'), date.strftime('%M'))

if __name__ == '__main__':
    show_all = False
    upto = 1
    username = None
    password = None
    for i in range(len(sys.argv)):
        arg = sys.argv[i]
        if arg == '-u':
            username = sys.argv[i + 1]
            i += 1
        elif arg == '-p':
            password = sys.argv[i + 1]
            i += 1
        elif arg == '-all':
            show_all = True
        elif arg == '-n':
            if sys.argv[i + 1].isdigit() and int(sys.argv[i + 1]) > 0:
                upto = sys.argv[i + 1]
                i += 1
            else:
                print('Usage: python3 timetable.py -u [USERNAME]* -p [PASSWORD]* (-n [LESSON INDEX] / -all)')
                sys.exit()
    print_info(int(upto), show_all, username, password)
