from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

today = datetime.now() + timedelta(hours=8)
start_date = os.getenv('START_DATE')
city = os.getenv('CITY')
birthday = os.getenv('BIRTHDAY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.getenv('TEMPLATE_ID')

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
  res = requests.get(url).json()
  return res['wea'], res['alarm'],res['aqi'], res['win'],res['win_speed'],res['tem'], res['tem2'], res['tem1'],res['air_tips']

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
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
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
weather,alarm,aqi,win,win_speed,tem,tem2,tem1,air_tips = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "words1.DATA":{
    "value":"今天又是元气满满的一天 ૮ ・ﻌ・ა"
  },
  "d1":{
    "value":"📅今天是："
  },
  "b1":{
    "value":"🕯距离你的生日还有"
  },
  "p1":{
    "value":"📈PM2.5："
  },
  "a1":{
    "value":"空气类型："
  },
  "c1":{
    "value":"🏙所在城市："
  },
  "w1":{
    "value":"🌤今天天气："
  },
  "t1":{
    "value":"🌡当前温度："
  },
  "l1":{
    "value":"今日最低温："
  },
  "h1":{
    "value":"⛽今日最高温："
  },
  "1":{
    "value":"今天是相遇的第"
  },
  "wi1":{
    "value":"🌀当前风向："
  },
  "words2.DATA":{
    "value":"📃寄语："
  },
  "city": {
    "value": city,
    "color": get_random_color()
  },
  "date": {
    "value": today.strftime('%Y年%m月%d日'),
    "color": get_random_color()
  },
  "weather": {
    "value": weather,
    "color": get_random_color()
  },
  "wind":{
    "value": win,
    "color": get_random_color()
  },
  "win_speed":{
    "value": win_speed,
    "color": get_random_color()
  },
  "pm25":{
    "value": aqi['pm25_desc'],
    "color": get_random_color()
  },
  "airQuality":{
    "value": aqi['air'],
    "color": get_random_color()
  },
  "temperature": {
    "value": tem,
    "color": get_random_color()
  },
  "highest": {
    "value": tem1,
    "color": get_random_color()
  },
  "lowest": {
    "value": tem2,
    "color": get_random_color()
  },
  "love_days": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "birthday_left": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "air_tips": {
    "value": air_tips,
    "color": get_random_color()
  },
  "alarm": {
    "value": alarm['alarm_content'],
    "color": get_random_color()
  },
  "words": {
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
