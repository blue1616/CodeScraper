import json
import datetime
import shutil
import time
import re
import os.path
from pymongo import MongoClient

client = None
db = None
collection = None
collection_channel = None

modules = [
  'github',
  'gist',
  'github_code',
  'gitlab',
  'gitlab_snippet',
  'google_custom',
  'pastebin',
  'rss_feed',
  'twitter'
]

github_settings = {
  'Target':'github',
  'Enable':True,
  'SearchLevel':1,
  'Time_Range':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

gist_settings = {
  'Target':'gist',
  'Enable':True,
  'Time_Range':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

github_code_settings = {
  'Target':'github_code',
  'Enable':True,
  'SearchLevel':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

gitlab_settings = {
  'Target':'gitlab',
  'Enable':True,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

gitlab_snippet_settings = {
  'Target':'gitlab_snippet',
  'Enable':True,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

pastebin_settings = {
  'Target':'pastebin',
  'Enable':True,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

google_custom_settings = {
  'Target':'google_custom',
  'Enable':True,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None',
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

rss_feed_settings = {
  'Target':'rss_feed',
  'Enable' : True,
  'Name' : 'None',
  'URL' : 'None',
  'Filters' : [],
  'Channel' : 'None',
  'Last_Post' : {'title':'None', 'link':'None', 'timestamp':'1970-01-01 00:00:00'},
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

twitter_settings = {
  'Target':'twitter',
  'Enable' : True,
  'Query' : 'None',
  'Users' : [],
  'Channel' : 'None',
  'Last_Post' : {'user':'None', 'text':'None', 'id':'None', 'link':'None'},
  '__MOD_ENABLE__' : True,
  '__INITIAL__' : True,
  '__SAFETY__': 0
}

setting_set = {
  'github':github_settings,
  'gist':gist_settings,
  'github_code':github_code_settings,
  'gitlab':gitlab_settings,
  'gitlab_snippet':gitlab_snippet_settings,
  'google_custom':google_custom_settings,
  'pastebin':pastebin_settings,
  'rss_feed':rss_feed_settings,
  'twitter':twitter_settings
}

def setDB(BD_HOST, DB_PORT, DB_NAME):
  global client
  global db
  global collection
  global collection_channel
  client = MongoClient(BD_HOST, DB_PORT)
  db = client[DB_NAME]
  collection = db['keywords']
  collection_channel = db['channels']


def setUsingChannels(channels):
  collection_channel.remove();
  if type(channels) == list:
    collection_channel.insert({'channels': channels})
    return True
  else:
    False

def getUsingChannels():
  channels = collection_channel.find()[0]
  return channels['channels']

def setDefaultSettings(target, default_dict):
  if target in modules:
    channels = getUsingChannels()
    setter = setting_set[target]
    for k in default_dict.keys():
      if k in setter.keys():
        if type(default_dict[k]) != type(setter[k]):
          return False
        if k == 'SearchLevel' and not default_dict['SearchLevel'] in [1,2]:
          return False
        if k == 'Channel' and not default_dict['Channel'] in channels:
          default_dict['Channel'] = channels[0]
        setter[k] = default_dict[k]
    setter['Index'] = 0
    setter['KEY'] = '__DEFAULT_SETTING__'
    collection.update({
            'Target':target,
            'KEY':'__DEFAULT_SETTING__'
        }, setter, upsert=True)
    return True
  else:
    return None

def isEnable(target):
  if target in modules:
    data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
    if data.count() != 0 and data[0]['__MOD_ENABLE__'] == True:
      return True
    else:
      return False
  else:
    return None

def disable(target):
  if target in modules:
    data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
    if data.count() != 0:
      updatedata = data[0]
      updatedata['__MOD_ENABLE__'] = False
      collection.update({
            'Target':target,
            'KEY':'__DEFAULT_SETTING__'
        }, updatedata)
      return True
    else:
      False
  else:
    return None

def setNewKeyword(target, word):
  if target in modules:
    default = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})[0]
    default['KEY'] = word
    del default['__MOD_ENABLE__'], default['_id'], default['__SAFETY__']
    if '__SEARCHEDPASTES__' in default.keys():
      del default['__SEARCHEDPASTES__']
    if 'Expire_date' in default:
      today = datetime.date.today()
      limit = (today + datetime.timedelta(int(default['Expire_date']))).strftime('%Y-%m-%d')
      default['Expire_date'] = limit
    replacedata = collection.find({'Target':target, 'KEY':word})
    if replacedata.count() == 0:
      index = collection.find({'Target':target}).sort('Index', -1)[0]['Index'] + 1
      default['Index'] = index
      collection.insert(default)
      return index
    else:
      index = collection.find({'Target':target, 'KEY':word})[0]['Index']
      default['Index'] = index
      collection.update({
            'Target':target,
            'KEY':word
        }, default)
      return index * -1
  else:
    return None

def removeKeyword(target, index):
  ret = None
  if target != 'rss_feed' and target in modules:
    data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0:
      key = data[0]['KEY']
      collection.remove({'Target':target, 'Index':index})
      ret = key
  return ret

def getAllState():
  result = {}
  for m in modules:
    default = collection.find({'Target':m, 'KEY':'__DEFAULT_SETTING__'})
    if default.count() == 0:
      result[m] = False
    else:
      result[m] = default[0]['__MOD_ENABLE__']
  return result

def enableKeywordSetting(target, index, enable):
  if target in modules:
    if target == 'rss_feed':
      data = collection.find({'Target':target, 'Name':index})
    else:
      data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0:
      if target == 'rss_feed':
        word = data[0]['Name']
        collection.update({'Target':target, 'Name':index}, {'$set': {'Enable': enable}})
      else:
        word = data[0]['KEY']
        collection.update({'Target':target, 'Index':index}, {'$set': {'Enable': enable}})
      return word
    else:
      return None
  else:
    None

def setSearchLevel(target, index, level):
  if target in modules:
    data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0 and 'SearchLevel' in data[0].keys():
      word = data[0]['KEY']
      collection.update({'Target':target, 'Index':index}, {'$set': {'SearchLevel': level}})
      return word
    else:
      return None
  else:
    return None

def setSearchRange(target, index, days):
  if target in modules:
    data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0 and 'Time_Range' in data[0].keys():
      word = data[0]['KEY']
      collection.update({'Target':target, 'Index':index}, {'$set': {'Time_Range': days}})
      return word
    else:
      return None
  else:
    return None

def setExpireDate(target, index, limit):
  if target in modules:
    data = collection.find({'Target':target, 'Index':index})
    regx = '\d{4}-(0[0-9]|1[0-2])-([0-2][0-9]|3[01])'
    if data.count() != 0 and 'Expire_date' in data[0].keys() and re.match(regx, limit):
      word = data[0]['KEY']
      collection.update({'Target':target, 'Index':index}, {'$set': {'Expire_date': limit}})
      return word
    else:
      return None
  else:
    return None

def setChannel(target, index, channel):
  if target in modules:
    if target == 'rss_feed':
      data = collection.find({'Target':target, 'Name':index})
    else:
      data = collection.find({'Target':target, 'Index':index})
    channels = getUsingChannels()
    if data.count() != 0 and channel in channels:
      if target == 'rss_feed':
        word = data[0]['Name']
        collection.update({'Target':target, 'Name':index}, {'$set': {'Channel': channel}})
        return word
      else:
        word = data[0]['KEY']
        collection.update({'Target':target, 'Index':index}, {'$set': {'Channel': channel}})
        return word
      return word
    else:
      return None
  else:
    None

def addExcludeList(target, index, exclude):
  if target in modules:
    data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0 and 'Exclude_list' in data[0].keys():
      word = data[0]['KEY']
      newlist = data[0]['Exclude_list'] + exclude
      collection.update({'Target':target, 'Index':index}, {'$set': {'Exclude_list': newlist}})
      return word
    else:
      return None
  else:
    return None

def clearExcludeList(target, index):
  if target in modules:
    data = collection.find({'Target':target, 'Index':index})
    if data.count() != 0 and 'Exclude_list' in data[0].keys():
      word = data[0]['KEY']
      collection.update({'Target':target, 'Index':index}, {'$set': {'Exclude_list': []}})
      return word
    else:
      return None
  else:
    return None

def getKeywords(target):
  if target in modules:
#    data = list(collection.find({'Target':target}))
    data = list(collection.find({"$and": [{"Target": target}, {"KEY": {"$ne": '__DEFAULT_SETTING__'}}]}).sort('Index'))
    return data
  else:
    return None

def getEnableKeywords(target):
  if target in modules:
    data = list(collection.find({"$and": [{"Target": target}, {"KEY": {"$ne": '__DEFAULT_SETTING__'}}, {'Enable': True}]}).sort('Index'))
    return data
  else:
    return None

def getKeyword(target, index):
  if target in modules:
    if target == 'rss_feed':
      data = collection.find({'Target':target, 'Name':index})
    else:
      data = collection.find({'Target':target, 'Index':index})
    if data.count() == 0:
      return None
    else:
      return data[0]
  else:
    return None

def getSafetyCount(target):
  if target in modules:
    data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
    if data.count() != 0:
      return data[0]['__SAFETY__']
    else:
      None
  else:
    return None

def setSafetyCount(target, count):
  if target in modules:
    data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
    if data.count() != 0:
      collection.update({'Target':target, 'KEY':'__DEFAULT_SETTING__'}, {'$set': {'__SAFETY__': count}})
      return True
    else:
      False
  else:
    return None

def setSearchedPastes(pastelist):
  target = 'pastebin'
  data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
  if data.count() != 0:
    collection.update({'Target':target, 'KEY':'__DEFAULT_SETTING__'}, {'$set': {'__SEARCHEDPASTES__': list(pastelist)}})
    return True
  else:
    False

def getSearchedPastes():
  target = 'pastebin'
  data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
  if data.count() != 0:
    if '__SEARCHEDPASTES__' in data[0].keys():
      return data[0]['__SEARCHEDPASTES__']
    else:
      return []
  else:
    False

def setNewRSSFeed(name, url):
  target = 'rss_feed'
  ret = False
  data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
  if data.count() != 0:
    if collection.count({'Target':target, 'Name':name}) == 0:
      default = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})[0]
      default['Name'] = name
      default['URL'] = url
      del default['__MOD_ENABLE__'], default['_id'], default['__SAFETY__'], default['KEY']
      collection.insert(default)
      ret = True
  return ret

def setNewRSSFilter(name, words, channel):
  target = 'rss_feed'
  data = collection.find({'Target':target, 'Name':name})
  ret = None
  if data.count() != 0:
    filters = data[0]['Filters']
    index = 0
    filter = {}
    for f in filters:
      if index < f['Index']:
        index = f['Index']
    filter['Index'] = index
    filter['Channel'] = data[0]['Channel']
    if channel in getUsingChannels():
      filter['Channel'] = channel
    filter['Words'] = words
    filters.append(filter)
    ret = index
    collection.update({'Target':target, 'Name':name}, {'$set': {'Filters': filters}})
  return ret

def editRSSFilter(name, index, words, channel):
  target = 'rss_feed'
  data = collection.find({'Target':target, 'Name':name})
  if data.count() != 0:
    filters = data[0]['Filters']
    filter = {}
    i = 0
    for f in filters:
      if index == f['Index']:
        filter = {'Index' : f['Index'],
          'Channel' : f['Channel'],
          'Words' : f['Words']}
        if channel != '':
          filter['Channel'] = channel
        if words != []:
          filter['Words'] = words
        filters[i] = filter
        ret = True
        break
      i += 1
    collection.update({'Target':target, 'Name':name}, {'$set': {'Filters': filters}})
    return True
  return False

def removeRSSFilter(name, index):
  target = 'rss_feed'
  data = collection.find({'Target':target, 'Name':name})
  ret = None
  if data.count() != 0:
    filters = data[0]['Filters']
    i = 0
    for f in filters:
      if index == f['Index']:
        ret = f['Words']
        filters.remove(f)
        break
    collection.update({'Target':target, 'Name':name}, {'$set': {'Filters': filters}})
  return ret

def haveSearched(target, name):
  keyword = 'rss_feed'
  if target == 'rss_feed':
    data = collection.find({'Target':target, 'Name':name})
  else:
    data = collection.find({'Target':target, 'Index':name})
  if data.count() != 0:
    if target == 'rss_feed':
      collection.update({'Target':target, 'Name':name}, {'$set': {'__INITIAL__': False}})
    else:
      collection.update({'Target':target, 'Index':name}, {'$set': {'__INITIAL__': False}})
    return True
  return False

def setRSSLastPost(name, post):
  target = 'rss_feed'
  data = collection.find({'Target':target, 'Name':name})
  if data.count() != 0:
    collection.update({'Target':target, 'Name':name}, {'$set': {'Last_Post': post}})
    return True
  return False

def setNewTwitterQuery(query, users):
  target = 'twitter'
  ret = False
  data = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})
  if data.count() != 0:
    default = collection.find({'Target':target, 'KEY':'__DEFAULT_SETTING__'})[0]
    del default['__MOD_ENABLE__'], default['_id'], default['__SAFETY__'], default['KEY']
    default['Query'] = query
    default['Users'] = users
    if users != []:
      default['KEY'] = query + ' Users: ' + ', '.join(users)
    else:
      default['KEY'] = query
    index = collection.find({'Target':target}).sort('Index', -1)[0]['Index'] + 1
    default['Index'] = index
    collection.insert(default)
    ret = index
  return ret

def editTwitterQuery(index, query, users):
  target = 'twitter'
  ret = None
  data = collection.find({'Target':target, 'Index':index})
  if data.count() != 0:
    tq = data[0]
    if query != '':
      collection.update({'Target':target, 'Index':index}, {'$set': {'Query': query}})
      ret = True
    else:
      query = tq['Query']
    if users != []:
      collection.update({'Target':target, 'Index':index}, {'$set': {'Users': users}})
      ret = True
    else:
      users = tq['Users']
    if ret:
      key = query + ' User: ' + ', '.join(users)
      collection.update({'Target':target, 'Index':index}, {'$set': {'KEY': key}})
      ret = key
  return ret

def addUserToTwitterQuery(index, users):
  target = 'twitter'
  ret = False
  data = collection.find({'Target':target, 'Index':index})
  if data.count() != 0:
    tq = data[0]
    if users != []:
      newlist = list(set(tq['Users'] + users))
      collection.update({'Target':target, 'Index':index}, {'$set': {'Users': newlist}})
      key = tq['Query'] + ' User: ' + ', '.join(newlist)
      collection.update({'Target':target, 'Index':index}, {'$set': {'KEY': key}})
      ret = key
  return ret

def setTwitterLastPost(index, post):
  target = 'twitter'
  data = collection.find({'Target':target, 'Index':index})
  if data.count() != 0:
    collection.update({'Target':target, 'Index':index}, {'$set': {'Last_Post': post}})
    return True
  return False
