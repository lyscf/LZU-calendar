from bs4 import BeautifulSoup
import requests
import pytz
from ics import Calendar, Event
from datetime import datetime

china_tz = pytz.timezone('Asia/Shanghai')
url = "http://jwk.lzu.edu.cn/academic/manager/coursearrange/studentWeeklyTimetable.do"

data = []


def get_data(weeknum):
    payload = {
        "yearid": "43",
        "termid": "2",
        "whichWeek": str(weeknum)
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://jwk.lzu.edu.cn",
        "Connection": "keep-alive",
        "Referer": "http://jwk.lzu.edu.cn/academic/manager/coursearrange/studentWeeklyTimetable.do",
        "Upgrade-Insecure-Requests": "1"
    }

    cookies = {
        "CASTGC": "FILL_IT",
        "iPlanetDirectoryPro": "FILL_IT",
        "JSESSIONID": "FILL_IT",
        "kaptchaCookie": "FILL_IT"
    }

    response = requests.post(url, data=payload, headers=headers, cookies=cookies).text
    print(response)

    soup = BeautifulSoup(response, 'html.parser')

    # 提取学年和周次信息
    year = soup.find('input', {'name': 'yearid'})['value']
    term = soup.find('input', {'name': 'termid'})['value']
    week = soup.find('select', {'name': 'whichWeek'}).text
    # 提取每天的课程信息
    for tr in soup.find_all('tr')[1:]:
        try:
            if tr:
                date = tr.find('td', {'name': 'td0'}).text
                course = tr.find('td', {'name': 'td1'}).text
                start_time = tr.find('td', {'name': 'td7'}).text
                end_time = tr.find('td', {'name': 'td8'}).text
                location = tr.find('td', {'name': 'td9'}).text + " " + tr.find('td', {'name': 'td10'}).text
                data.append(
                    {'date': date, "course": course, "start_time": start_time, "end_time": end_time,
                     "location": location})
        except:
            pass  # 忽略解析异常的行


i = 5
while i <21:
    get_data(i)
    i = i +1

print(data)
china_tz = pytz.timezone('Asia/Shanghai')

c = Calendar()

for line in data:
    start = datetime.strptime(line['date'] + ' ' + line['start_time'], '%Y-%m-%d %H:%M').astimezone(china_tz)
    end = datetime.strptime(line['date'] + ' ' + line['end_time'], '%Y-%m-%d %H:%M').astimezone(china_tz)
    print(start)
    print(end)
    event = Event()

    # 设置开始时间
    event.begin = start

    # 设置结束时间
    event.end = end

    event.name = line['course']
    event.location = line['location']
    event.uid = line['course'] + "_" + start.strftime("%Y%m%d%H%M")
    c.events.add(event)

with open('calendar.ics', 'wb') as f:
    ical = str(c)
    f.write(ical.encode('utf-8'))
