from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now() + timedelta(hours=8)
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "https://v0.yiketianqi.com/api?unescape=1&version=v61&appid=39381872&appsecret=h1fMpbU1=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp']), weather['wind'], math.floor(weather['pm25']),  weather['airQuality'], math.floor(weather['low']), math.floor(weather['high'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, wind, pm25, airQuality, lowest, highest = get_weather()
data = {"words2":{"value":"今天又是元气满满的一天 ૮ ・ﻌ・ა"},"date1":{"value":"📅今天是："},"date":{"value":today.strftime('%Y年%m月%d日'),"color":get_random_color()},"weather1":{"value":"⛅今天天气："},"weather":{"value":wea,"color":get_random_color()},"city1":{"value":"🌆所在城市："},"city":{"value":city,"color":get_random_color()},"temperature1":{"value":"📉当前温度："},"temperature":{"value":temperature,"color":get_random_color()},"temperature2":{"value":"℃"},"wind1":{"value":"🌀当前风向："},"wind":{"value":wind,"color":get_random_color()},"pm251":{"value":"📈PM2.5："},"pm25":{"value":pm25,"color":get_random_color()},"airQuality1":{"value":"空气类型："},"airQuality":{"value":airQuality,"color":get_random_color()},"lowest1":{"value":"今日最低温："},"lowest": {"value":lowest,"color":get_random_color()},"highest1":{"value":"⛽今日最高温："},"highest":{"value": highest, "color":get_random_color()},"love_days1":{"value":"今天是相遇的第"},"love_days":{"value":get_count(),"color":get_random_color()},"birthday_left1":{"value":"🕯距离你的生日还有"},"birthday_left":{"value":get_birthday(),"color":get_random_color()},"words1":{"value":"📃寄语："},"words":{"value":get_words(),"color":get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
