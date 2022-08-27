import math
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import datetime

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
  res1 = requests.get(url).json()
  return res1['week'],res1['wea'], res1['alarm'],res1['aqi'], res1['win'],res1['win_speed'],res1['tem'], res1['tem2'], res1['tem1'],res1['air_tips']

def get_weather_wea():
  url = "http://api.tianapi.com/tianqi/index?key=d5edced4967c76fd11899dbe1b753d91&city=" + city
  res2 = requests.get(url).json()
  res21 = res2['newslist'][0]
  return res21['sunrise'],res21['sunset'],res21['tips']

def get_lunar_calendar():
  today = datetime.datetime.now()
  date = today
  url = "http://api.tianapi.com/lunar/index?key=d5edced4967c76fd11899dbe1b753d91&date=" + date
  lunar_calendar = requests.get(url).json()
  res3 = lunar_calendar['newslist'][0]
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
week,weather,alarm,aqi,win,win_speed,tem,tem2,tem1,air_tips = get_weather()
sunrise,sunset,tips = get_weather_wea()
lubarmonth,lunarday,jieqi,lunar_festival,festival = get_lunar_calendar()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "wo1":{
    "value":""
  },
  "d1":{
    "value":""
  },
  "b1":{
    "value":""
  },
  "a1":{
    "value":""
  },
  "c1":{
    "value":""
  },
  "w1":{
    "value":""
  },
  "t1":{
    "value":""
  },
  "s1":{
    "value":""
  },
  "s2":{
    "value":""
  },
  "l1":{
    "value":""
  },
  "h1":{
    "value":""
  },
  "1":{
    "value":""
  },
  "wi1":{
    "value":""
  },
  "ws2":{
    "value":""
  },
  "cy": {
    "value": city,
    "color": get_random_color()
  },
  "se": {
    "value": sunrise,
    "color": get_random_color()
  },
  "st": {
    "value": sunset,
    "color": get_random_color()
  },
  "wk": {
    "value": week,
    "color": get_random_color()
  },
  "de": {
    "value":today.strftime('%Y年%m月%d日'),
    "color": get_random_color()
  },
  "wr": {
    "value": weather,
    "color": get_random_color()
  },
  "luh": {
    "value": lubarmonth,
    "color": get_random_color()
  },
  "luy": {
    "value": lunarday,
    "color": get_random_color()
  },
  "jie": {
    "value": jieqi,
    "color": get_random_color()
  },
  "l_fel": {
    "value": lunar_festival,
    "color": get_random_color()
  },
   "fel": {
    "value": festival,
    "color": get_random_color()
  },
  "wd":{
    "value": win,
    "color": get_random_color()
  },
  "win_d":{
    "value": win_speed,
    "color": get_random_color()
  },
  "ay":{
    "value": aqi['air_level'],
    "color": get_random_color()
  },
  "te": {
    "value": tem,
    "color": get_random_color()
  },
  "ht": {
    "value": tem1,
    "color": get_random_color()
  },
  "lt": {
    "value": tem2,
    "color": get_random_color()
  },
  "l_ds": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "b_lt": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "a_ts": {
    "value": air_tips,
    "color": get_random_color()
  },
  "ts": {
    "value": tips,
    "color": get_random_color()
  },
  "a_ct": {
    "value": alarm['alarm_title'],
    "color": get_random_color()
  },
  "ws": {
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
