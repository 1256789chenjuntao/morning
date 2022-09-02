from datetime import date, datetime, timedelta
from collections import defaultdict
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
from borax.calendars.lunardate import LunarDate
from random import randint
import math
import requests
import os
import re
import random
import emoji

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期
today1 = LunarDate.today()

city = os.getenv('CITY')
start_date = os.getenv('START_DATE')
birthday = os.getenv('BIRTHDAY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.getenv('TEMPLATE_ID')

#为读取农历生日准备
lubaryear1 = today1.year
n = int(birthday[0:4:1])#读取无用，为理解下面两行留着，可删去
y = int(birthday[5:7])#切片
r = int(birthday[8:])
birthday1 = LunarDate(lubaryear1, y, r)#构建农历日期
birthday2 = birthday1.to_solar_date()#转化成公历日期，输出为字符串

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_ids:
  print('请设置 USER_ID，若存在多个 ID 用空格分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID')
  exit(422)

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
  if city is None:
    print('请设置城市')
    return None
  url = "https://v0.yiketianqi.com/api?unescape=1&version=v61&appid=78158848&appsecret=650ylFRx&city=" + city
  res1 = requests.get(url,verify=False)
  if res1.status_code != 200:
    return res1()
  res11 = res1.json()
  return res11['week'],res11['alarm'],res11['aqi'], res11['win'],res11['win_speed'],res11['tem'], res11['tem2'], res11['tem1'],res11['air_tips']

#天行数据接口
def get_weather_wea():
  url = "http://api.tianapi.com/tianqi/index?key=d5edced4967c76fd11899dbe1b753d91&city=" + city
  res2 = requests.get(url,verify=False)
  if res2.status_code != 200:
    return res2()
  res21 = res2.json()['newslist'][0]
  return res21['sunrise'],res21['sunset'],res21['tips'],res21['weather'],res21['pop']

#疫情接口，还没有调试成功，可删除
def get_Covid_19():
  url = "https://interface.sina.cn/news/wap/fymap2020_data.d.json"
  res3 = requests.get(url)
  if res3.status_code != 200:
    return res3()
  res32 = res3.json()['data']['list'][16]['city'][10]
  return res32['econNum'],res32['asymptomNum']

#农历接口
def get_lunar_calendar():
  date = today.strftime("%Y-%m-%d")
  url = "http://api.tianapi.com/lunar/index?key=d5edced4967c76fd11899dbe1b753d91&date=" + date
  lunar_calendar = requests.get(url,verify=False)
  if lunar_calendar.status_code != 200:
    return get_lunar_calendar()
  res3 = lunar_calendar.json()['newslist'][0]
  return res3['lubarmonth'],res3['lunarday'],res3['jieqi'],res3['lunar_festival'],res3['festival']

# 纪念日正数
def get_memorial_days_count():
  if start_date is None:
    print('没有设置 START_DATE')
    return 0
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(birthday2.strftime("%Y-%m-%d"), "%Y-%m-%d")#先转换成datetime.date类型,再转换成datetime.datetime
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
week,alarm1,aqi,win,win_speed,tem,tem1,tem2,air_tips = get_weather()
sunrise,sunset,tips,weather,pop = get_weather_wea()
lubarmonth,lunarday,jieqi,lunar_festival,festival = get_lunar_calendar()
econNum,asymptomNum = get_Covid_19()
alarm2 = alarm1.get('alarm_title')

def get_weather_icon(weather):
    weather_icon = "🌈"
    weather_icon_list = ["☀️",  "☁️", "⛅️",
                         "☃️", "⛈️", "🏜️", "🏜️", "🌫️", "🌫️", "🌪️", "🌧️"]
    weather_type = ["晴", "阴", "云", "雪", "雷", "沙", "尘", "雾", "霾", "风", "雨"]
    for index, item in enumerate(weather_type):
        if re.search(item, weather):
            weather_icon = weather_icon_list[index]
            break
    return weather_icon

if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "1":{
    "value":"",
  },
  "2":{
    "value":"",
  },
  "3": {
    "value":today.strftime('%Y年%m月%d日')+week,
    "color": get_random_color()
  },
  "4": {
    "value": lubarmonth+lunarday+jieqi+lunar_festival+festival,
    "color": get_random_color()
  },
  "5":{
    "value":"",
  },
  "6": {
    "value": get_weather_icon(weather)+weather,
    "color": get_random_color()
  },
  "7":{
    "value":"",
  },
  "8": {
    "value": city,
    "color": get_random_color()
  },
  "9":{
    "value":"",
  },
  "a": {
    "value": tem,
    "color": get_random_color()
  },
  "b":{
    "value":"",
  },
   "c": {
    "value": tem1+"℃"+"~"+tem2+"℃",
    "color": get_random_color()
  },
  "d":{
    "value":"",
  },
  "e": {
    "value": sunrise,
    "color": get_random_color()
  },
  "f":{
    "value":"",
  },
  "g": {
    "value": sunset,
    "color": get_random_color()
  },
  "h":{
    "value":"",
  },
  "i":{
    "value": win+win_speed,
    "color": get_random_color()
  },
  "j":{
    "value":"",
  },
  "k":{
    "value": pop+"%",
    "color": get_random_color()
  },
  "l":{
    "value":"",
  },
  "m":{
    "value": aqi['air_level'],
    "color": get_random_color()
  },
  "n":{
    "value":"",
  },
  "o": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "p":{
    "value":"",
  },
  "q": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "r":{
    "value":"",
  },
  "s": {
    "value": "",
    "color": get_random_color()
  },
  "t":{
    "value":"",
  },
  "u": {
    "value": tips,
    "color": get_random_color()
  },
  "v": {
    "value": alarm2,
    "color": get_random_color()
  },
  "w":{
    "value":"",
    "color": get_random_color()
  },
  "x":{
    "value":"澄迈新增"+asymptomNum+"例，"+"累计"+econNum+"例",
    "color": get_random_color()
  },
  "y": {
    "value": "",
    "color": get_random_color()
  },
  "z":{
    "value": get_words(),
    "color": get_random_color()
  },
}

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")
