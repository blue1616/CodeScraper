# -*- coding: utf-8 -*-
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re
from . import edit_conf_db as ec
import os.path
import requests
import feedparser
import lxml.html

targets = [
  'github',
  'github_code',
  'gist',
  'gitlab',
  'gitlab_snippet',
  'pastebin',
  'google_custom',
  'rss_feed',
  'twitter'
]

def getPostData(keyword, index, target):
  post_data = ''
  if index > 0:
    post_data = 'Set New Search Keyword : `{keyword}` (index : {index}) in _{target}_'.format(keyword=keyword, index=abs(index), target=target)
  elif index < 0:
    post_data = 'Initialize Search Keyword : `{keyword}` (index : {index}) in _{target}_'.format(keyword=keyword, index=abs(index), target=target)
  else:
    post_data = 'Error has Occured'
  return post_data

def getEnabledTargets():
  etargets = []
  state = ec.getAllState()
  for name,enable in state.items():
    if enable:
      etargets.append(name)
  return etargets

@respond_to('setKeyword: (.*)')
@respond_to('setK: (.*)')
def setKeyword(message, params):
  target = ''
  enabled = getEnabledTargets()
  targets.append('all')
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled or target == 'all':
    word = params.split(';')[0].strip()
    post_data = ''
    if word == '':
      post_data = 'Please Put a Word'
    else:
      setter = [
        'github',
        'github_code',
        'gist',
        'gitlab'
      ]
      if target in enabled:
        ret = ec.setNewKeyword(target, word)
        post_data = getPostData(word, ret, target)
      elif target == 'all':
        enabled = list(set(enabled) & set(setter))
        for s in enabled:
          ret = ec.setNewKeyword(s, word)
          if ret != 0:
            if post_data != '':
              post_data += '\n'
            post_data += getPostData(word, ret, s)
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('removeKeyword: (.*)')
@respond_to('removeK: (.*)')
def removeKeyword(message, params):
  target = ''
  enabled = getEnabledTargets()
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  post_data = ''
  if target in enabled:
    params = params.split(';')[0].strip()
    if params.isdigit():
      index = int(params.strip())
      ret = ec.removeKeyword(target, index)
      if ret != None:
        post_data = '`{key}`(index : {index}) is removed in _{target}_'.format(key=ret, index=str(index), target=target)
      else:
        post_data = 'No Data'
    else:
      post_data = 'Please Put Index of the Keyword'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('disableKeyword: (.*)')
@respond_to('disableK: (.*)')
def disableKeyword(message, params):
  target = ''
  enabled = getEnabledTargets()
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled:
    params = params.split(';')[0]
    if (target != 'rss_feed' and params.strip().isdigit()) or target == 'rss_feed':
      if target != 'rss_feed':
        index = int(params.strip())
      else:
        index = params.strip()
      ret = ec.enableKeywordSetting(target, index, False)
      if ret == None:
        post_data = 'No Data'
      else:
        post_data = '`{keyword}` is disabled in _{target}_'.format(keyword=ret, target=target)
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('enableKeyword: (.*)')
@respond_to('enableK: (.*)')
def enableKeyword(message, params):
  target = ''
  enabled = getEnabledTargets()
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled:
    params = params.split(';')[0]
    if (target != 'rss_feed' and params.strip().isdigit()) or target == 'rss_feed':
      if target != 'rss_feed':
        index = int(params.strip())
      else:
        index = params.strip()
      ret = ec.enableKeywordSetting(target, index, True)
      if ret == None:
        post_data = 'No Data'
      else:
        post_data = '`{keyword}` is enabled in _{target}_'.format(keyword=ret, target=target)
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setSearchLevel: (.*)')
@respond_to('setSL: (.*)')
def setSearchLevel(message, params):
  target = ''
  enabled = getEnabledTargets()
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  words = params.strip().split(';')
  valid_targets = [
    'github',
    'github_code'
  ]
  if target in valid_targets and target in enabled:
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        if words[1].strip().isdigit():
          valid_num = [1, 2, 3, 4]
          if int(words[1].strip()) in valid_num:
            ret = ec.setSearchLevel(target, index, int(words[1].strip()))
            if ret == '':
              post_data = 'No Data'
            else:
              post_data = 'Set `{keyword}` Search Level to {level}'.format(keyword=ret, level=words[1].strip())
          else:
            post_data = 'Invalid Search Level'
        else:
          post_data = 'Please Put Index of the Word'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setSearchTimeRange: (.*)')
@respond_to('setSTR: (.*)')
def setSearchTimeRange(message, params):
  enabled = getEnabledTargets()
  target = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  words = params.strip().split(';')
  valid_targets = [
    'github',
    'gist'
  ]
  if target in valid_targets and target in enabled:
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        if words[1].strip().isdigit():
          ret = ec.setSearchRange(target, index, int(words[1].strip()))
          if ret == '':
            post_data = 'No Data'
          else:
            post_data = '`{keyword}` serach in _{target}_ in last {range} days'.format(keyword=ret, target=target, range=words[1].strip())
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setExpireDate: (.*)')
@respond_to('setED: (.*)')
def setExpireDate(message, params):
  enabled = getEnabledTargets()
  target = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  words = params.strip().split(';')
  if 'rss_feed' in enabled:
    enabled.remove('rss_feed')
  if target in enabled:
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        regx = '\d{4}-(0[0-9]|1[0-2])-([0-2][0-9]|3[01])'
        if re.match(regx, words[1].strip()):
          ret = ec.setExpireDate(target, index, words[1].strip())
          if ret == '':
            post_data = 'No Data'
          else:
            post_data = '`{keyword}` in _{target}_ will expire at {date}'.format(keyword=ret, target=target, date=words[1].strip())
        else:
          post_data = 'Parameter Pattern not Match'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setChannel: (.*)')
@respond_to('setC: (.*)')
def setChannel(message, params):
  base = os.path.dirname(os.path.abspath(__file__))
  channelfile = os.path.normpath(os.path.join(base, '../settings/channellist'))
  enabled = getEnabledTargets()
  target = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled:
    words = params.strip().split(';')
    if (target != 'rss_feed' and words[0].strip().isdigit()) or target == 'rss_feed':
      if target != 'rss_feed':
        index = int(words[0].strip())
      else:
        index = words[0].strip()
      if len(words) > 1:
        channels = ec.getUsingChannels()
        if words[1].strip() in channels:
          ret = ec.setChannel(target, index, words[1].strip())
          if ret == '':
            post_data = 'No Data'
          else:
            post_data = '`{keyword}` result in _{target}_ will notify at {channel}'.format(keyword=ret, target=target, channel=words[1].strip())
        else:
          post_data = 'Parameter Pattern not Match'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('addExcludeList: (.*)')
@respond_to('addEL: (.*)')
def addExcludeList(message, params):
  target = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  words = params.strip().split(';')
  valid_targets = [
    'github',
    'github_code',
    'gist',
    'gitlab',
    'gitlab_snippet',
    'google_custom'
  ]
  enabled = list(set(getEnabledTargets()) & set(valid_targets))
  if target in enabled:
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        for word in words[1:]:
          if word != '':
            ret = ec.addExcludeList(target, index, word)
            if ret == '':
              post_data = 'No Data'
              break
            else:
              post_data = 'Add {words} in Exclude List of `{keyword}` in _{target}_'.format(words=','.join(words[1:]), keyword=ret, target=target)
          else:
            post_data = 'No Data'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('clearExcludeList: (.*)')
@respond_to('clearEL: (.*)')
def clearExcludeList(message, params):
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  valid_targets = [
    'github',
    'github_code',
    'gist',
    'gitlab',
    'gitlab_snippet',
    'google_custom'
  ]
  enabled = list(set(getEnabledTargets()) & set(valid_targets))
  params = params.split(';')[0]
  if target in enabled:
    if params.strip().isdigit():
      index = int(params.strip())
      ret = ec.clearExcludeList(target, index)
      if ret == None:
        post_data = 'No Data'
      else:
        post_data = 'Delete All Exclude List of `{keyword}` in _{target}_'.format(keyword=ret, target= target)
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('getKeyword: (.*)')
@respond_to('getK: (.*)')
def getKeyword(message, params):
  post_data = ''
  target = 'all'
  targets.append('all')
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  enabled = getEnabledTargets()
  if target in enabled or target == 'all':
    for g in enabled:
      if target == g or target == 'all':
        keys = ec.getEnableKeywords(g)
        if keys != []:
          if g == 'rss_feed':
            post_data += '-- Enabled RSS Feeds --\n'
            for k in keys:
              post_data += str(k['Name']) + ' : `' + k['URL'] + '`\n'
          else:
            post_data += '-- Enabled Search Keyword in _{target}_ --\n'.format(target=g)
            for k in keys:
              post_data += str(k['Index']) + ' : `' + k['KEY'] + '`\n'
  else:
    post_data = 'Invalid Target'
  if post_data == '':
    post_data = 'I don\'t have any data yet'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('getAllKeyword: (.*)')
@respond_to('getAllK: (.*)')
def getAllKeyword(message, params):
  post_data = ''
  target = 'all'
  targets.append('all')
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  enabled = getEnabledTargets()
  if target in enabled or target == 'all':
    for g in enabled:
      if target == g or target == 'all':
        keys = ec.getKeywords(g)
        if keys != []:
          if g == 'rss_feed':
            post_data += '-- Enabled RSS Feeds --'
            for k in keys:
              post_data += str(k['Name']) + ' : `' + k['URL'] + '`\n'
          else:
            post_data += '-- Enabled Search Keyword in _{target}_ --\n'.format(target=g)
            for k in keys:
              post_data += str(k['Index']) + ' : `' + k['KEY'] + '`\n'
  else:
    post_data = 'Invalid Target'
  if post_data == '':
    post_data = 'I don\'t have any data yet'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('getSearchSetting: (.*)')
@respond_to('getSS: (.*)')
def getKeywordSetting(message, params):
  post_data = ''
  target = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  params = params.split(';')[0]
  enabled = getEnabledTargets()
  if target in enabled:
    if target == 'rss_feed':
      keyword = ec.getKeyword(target, params.strip())
      if keyword == None:
        post_data = 'No Data'
      else:
        conf_params = [
          'Enable',
          'URL',
          'Filters',
          'Channel',
          'Last_Post'
        ]
        post_data = 'Settings of `' + keyword['Name'] + '` is :\n```'
        for p in conf_params:
          if p == 'Filters':
            v = ''
            for f in keyword['Filters']:
              v += '\n\tINDEX: ' + str(f['Index']) + '\n'
              v += '\tWORDS: ' + ', '.join(f['Words']) + '\n'
              v += '\tCHANNEL: ' + f['Channel']
          else:
            v = keyword[p]
          post_data += p.upper().replace('_', ' ') + ': ' + str(v) + '\n'
        post_data += '```'
    else:
      if params.strip().isdigit():
        index = int(params.strip())
        keyword = ec.getKeyword(target, index)
        if keyword == None:
          post_data = 'No Data'
        else:
          conf_params = [
            'Index',
            'Enable',
            'Query',
            'Users',
            'SearchLevel',
            'Time_Range',
            'Expire_date',
            'Channel',
            'Last_Post'
          ]
          post_data = 'Settings of `' + keyword['KEY'] + '` is :\n```'
          for p in conf_params:
            if p in keyword.keys():
              v = keyword[p]
              post_data += p.upper().replace('_', ' ') + ': ' + str(v) + '\n'
          post_data += '```'
      else:
        post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

def isMatched(word, text):
  symbols = r'[!\"#$%&\'()*+,\-./:;<=>@\[\]^_{|}~\\]'
  re_symbol = re.compile(symbols)
  repatt = False
  matched = True
  if re.search(re_symbol, word):
    if re.search(patt, text):
      matched = True
    else:
      matched = False
  else:
    for p in word.split(' '):
      if text.lower().find(p.lower()) < 0:
        matched = False
  return matched

@respond_to('reMatchTest: (.*)')
def reMatchTest(message, params):
  post_data = ''
  target = 'pastebin'
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target == 'pastebin' or target == 'gitlab_snippet':
    words = params.strip().split(';')
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        candidatelist = ec.getKeywordlist(target)
        if index in candidatelist.values():
          key = ''
          for k,v in candidatelist.items():
            if v == index:
              key = k
              break
          word = words[1].strip()
          post_data = ''
          if re.match('[a-zA-Z0-9]{8}', word):
            post_data += 'Found Pastebin id pattern.\n'
            word = 'https://pastebin.com/raw/' + word
            raw_result = requests.get(word, timeout=10)
            if raw_result.status_code == 200:
              if isMatched(key, raw_result.text):
                post_data += 'The pattern, `{keyword}` match to contents of {url}'.format(keyword=key, url=word)
              else:
                post_data += 'The pattern, `{keyword}` not match to contents of {url}'.format(keyword=key, url=word)
            else:
              post_data += 'I couldn\'t access to {url}'.format(url=word)
          else:
            if isMatched(key, raw_result.text):
              post_data += 'The pattern, `{keyword}` match'.format(keyword=key)
            else:
              post_data += 'The pattern, `{keyword}` not match'.format(keyword=key)
        else:
          post_data = 'No Data'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Word'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

def checkRSSUrl(url):
  try:
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    response = requests.get(url, timeout=4, headers=headers)
    rss = feedparser.parse(response.text)
    rssurl = None
    if rss['version'] == 'rss10' or rss['version'] == 'rss20' or rss['version'] == 'atom10':
      rssurl = url
    else:
      root = lxml.html.fromstring(response.text)
      for link in root.xpath('//link[@type="application/rss+xml"]'):
        url = link.get('href')
      rss = feedparser.parse(url)
      if rss['version'] == 'rss10' or rss['version'] == 'rss20' or rss['version'] == 'atom10':
        rssurl = url
    return rssurl
  except:
    return None

@respond_to('setFeed: (.*)')
@respond_to('setF: (.*)')
def setNewFeed(message, params):
  target = ''
  enabled = getEnabledTargets()
  if 'rss_feed' in enabled:
    name = params.split(';')[0].strip()
    post_data = ''
    if name == '':
      post_data = 'Please Put a Name'
    else:
      url = ''
      if len(params) > params.find(';')+1:
        url = params[params.find(';')+1:].strip()
      if url == '':
        post_data = 'Please Put URL if RSS Feed'
      patt = r'https?://[A-Za-z0-9\-.]{0,62}?\.([A-Za-z0-9\-.]{1,255})/?[A-Za-z0-9.\-?=#%/]*'
      url = re.search(patt, url).group(0)
      rssurl = checkRSSUrl(url)
      if rssurl == None:
        post_data = 'Invalid RSS URL'
      else:
        if url != rssurl:
          post_data += 'RSS Feed Found. '
        ret = ec.setNewRSSFeed(name, rssurl)
        if not ret:
          post_data = '{name} is already used'.format(name=name)
        else:
          post_data += 'Set `{url}` to _{name}_'.format(url=rssurl, name=name)
  else:
    post_data = 'RSS is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setFeedFilter: (.*)')
@respond_to('setFF: (.*)')
def setFeedFilter(message, params):
  target = ''
  enabled = getEnabledTargets()
  if 'rss_feed' in enabled:
    words = params.split(';')
    post_data = ''
    if len(words) < 2:
      post_data = 'Parameter Shortage'
    else:
      name = words[0].strip()
      filter = []
      for w in words[1].split(' '):
        if w.strip() != '':
          filter.append(w.strip())
      channel = ''
      if len(words) > 2:
        channel = words[2].strip()
      ret = ec.setNewRSSFilter(name, filter, channel)
      if ret != None:
        post_data = 'New Filter `[{filter}]`(index : {index}) is set to _{name}_'.format(filter=', '.join(filter), name=name, index=ret)
      else:
        post_data = 'Error has Occured'
  else:
    post_data = 'RSS is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('editFeedFilter: (.*)')
@respond_to('editFF: (.*)')
def editFeedFilter(message, params):
  enabled = getEnabledTargets()
  if 'rss_feed' in enabled:
    words = params.split(';')
    post_data = ''
    if len(words) < 4:
      post_data = 'Parameter Shortage'
    else:
      name = words[0].strip()
      if words[1].strip().isdigit():
        filter = []
        index = int(words[1].strip())
        for w in words[2].split(' '):
          if w != '':
            filter.append(w.strip())
        channel = ''
        if len(words) > 3:
          channel = words[3].strip()
        ret = ec.editRSSFilter(name, index, filter, channel)
        if ret:
          post_data = '`[{filter}]`(index : {index}) is set in _{name}_'.format(filter=', '.join(filter), index=index, name=name)
        else:
          post_data = 'Error has Occured'
      else:
        post_data = 'Please Put Index of the Filter'
  else:
    post_data = 'RSS is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('removeFeedFilter: (.*)')
@respond_to('removeFF: (.*)')
def removeFeedFilter(message, params):
  enabled = getEnabledTargets()
  if 'rss_feed' in enabled:
    words = params.split(';')
    post_data = ''
    if len(words) < 2:
      post_data = 'Parameter Shortage'
    else:
      name = words[0].strip()
      if words[1].strip().isdigit():
        index = int(words[1].strip())
        ret = ec.removeRSSFilter(name, index)
        if ret != None:
          post_data = '`[{filter}]`(index : {index}) is removed in _{name}_'.format(filter=', '.join(ret), name=name, index=index)
        else:
          post_data = 'Error has Occured'
      else:
        post_data = 'Please Put Index of the Filter'
  else:
    post_data = 'RSS is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('setTwitterQuery: (.*)')
@respond_to('setTQ: (.*)')
def setTwitterQuery(message, params):
  target = ''
  enabled = getEnabledTargets()
  if 'twitter' in enabled:
    words = params.split(';')
    post_data = ''
    users = []
    query = ''
    continueflag = True
    if len(words) == 1:
      if words[0].strip() != '':
        query = words[0].strip()
      else:
        post_data = 'Query is Empty'
        continueflag = False
    elif len(words) > 1:
      if words[0].strip() != '' or words[1].strip() != '':
        query = words[0].strip()
        for u in words[1].split(' '):
          if u.strip() != '':
            users.append(u.strip())
      else:
        post_data = 'Query is Empty'
        continueflag = False
    else:
      post_data = 'Parameter Shortage'
      continueflag = False
    if continueflag:
      name = words[0].strip()
      ret = ec.setNewTwitterQuery(query, users)
      if ret != None:
        if users != []:
          key = query + ' Users: ' + ', '.join(users)
        else:
          key = query
        post_data = 'New Twitter Search Query `[{query}]`(index : {index}) was set'.format(query=key, index=ret)
      else:
        post_data = 'Error has Occured'
  else:
    post_data = 'Twitter is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('editTwitterQuery: (.*)')
@respond_to('editTQ: (.*)')
def editTwitterQuery(message, params):
  enabled = getEnabledTargets()
  if 'twitter' in enabled:
    post_data = ''
    params = params.split(';')
    index = params[0].strip()
    if index.isdigit():
      index = int(index)
      if len(params) == 2:
        ret = ec.editTwitterQuery(index, params[1].strip(), [])
        if ret != None:
          post_data = '`{key}` was set in TwitterQuery (index : {index})'.format(key=ret, index=str(index))
        else:
          post_data = 'No Data'
      elif len(params) > 2:
        users = []
        for u in params[2].strip().split(' '):
          if u.strip() != '':
            users.append(u.strip())
        ret = ec.editTwitterQuery(index, params[1].strip(), users)
        if ret != None:
          post_data = '`{key}` was set in TwitterQuery (index : {index})'.format(key=ret, index=str(index))
        else:
          post_data = 'No Data'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Keyword'
  else:
    post_data = 'Twitter is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('addUserTwitterQuery: (.*)')
@respond_to('addUserTQ: (.*)')
def addUserTwitterQuery(message, params):
  enabled = getEnabledTargets()
  if 'twitter' in enabled:
    post_data = ''
    params = params.split(';')
    index = params[0].strip()
    if index.isdigit():
      index = int(index)
      if len(params) > 1:
        users = []
        for u in params[1].strip().split(' '):
          if u.strip() != '':
            users.append(u.strip())
        ret = ec.addUserToTwitterQuery(index, users)
        if ret != None:
          post_data = '`{key}` was set in TwitterQuery (index : {index})'.format(key=ret, index=str(index))
        else:
          post_data = 'No Data'
      else:
        post_data = 'Parameter Shortage'
    else:
      post_data = 'Please Put Index of the Keyword'
  else:
    post_data = 'Twitter is not enabled'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('removeTwitterQuery: (.*)')
@respond_to('removeTQ: (.*)')
def removeTwitterQuery(message, params):
  target = 'twitter'
  enabled = getEnabledTargets()
  post_data = ''
  if target in enabled:
    params = params.split(';')[0].strip()
    if params.isdigit():
      index = int(params.strip())
      ret = ec.removeKeyword(target, index)
      if ret != None:
        post_data = '`{key}`(index : {index}) is removed in _twitter_'.format(key=ret, index=str(index))
      else:
        post_data = 'No Data'
    else:
      post_data = 'Please Put Index of the Keyword'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('help:')
def getAllKeyword(message):
#  candidatelist = setting.getKeywordlist()
  post_data = '''```Command Format is Following:
\t{Command}: {target}; {arg1}; {arg2}; ...

Command List:

\'setKeyword: target; [word]\'\tAdd [word] as New Search Keyword with Default Settings.
 (abbreviation=setK:)
\'removeKeyword: target; [index]\'tRemove the Search Keyword indicated by [index].
 (abbreviation=removeK:)
\'enableKeyword: target; [index]\'\tEnable the Search Keyword indicated by [index].
 (abbreviation=enableK:)
\'disableKeyword: target; [index]\'\tDisable the Search Keyword indicated by [index].
 (abbreviation=disableK:)
\'setSearchLevel: target; [index]\'\tSet Search Level of Github Search (1-4) or Gihub Code Search (1-2) indicated by [index].
 (abbreviation=setSL:)
\'setExpireDate: target; [index]; [expiration date]\'\tSet a Expiration Date of the Keyword indicated by [index]. [expiration date] Format is YYYY-mm-dd.
 (abbreviation=setED:)
\'setChannel: target; [index];[channel]\'\tSet channel to notify the Search Keyword\'s result.
 (abbreviation=setC:)
\'getKeyword: target;\'\tListing Enabled Search Keywords.
 (abbreviation=getK:)
\'getAllKeyword: target;\'\tListing All Search Keyword (include Disabled Keywords).
 (abbreviation=getAllK:)
\'getSearchSetting: target; [index]\'\tShow Setting of the Search Keyword indicated by [index].
 (abbreviation=getSS:)

\'reMatchTest: target; [index]; [text]\'\tCheck wheaer the pattern indicated by [index] in [target] matches [text]. If set pattern to Pastebin ID, check the contens of pastebin.
\'setFeed: [name]; [url]\'\tAdd RSS Feed to [url] as [name].
 (abbreviation=setF:)
\'setFeedFilter: [name]; [filter]\'\tAdd new RSS Feed Filter. Notily only contains filter words.
 (abbreviation=setFF:)
\'editFeedFilter: [name]; [index]; filter\'\tEdit Feed Filter indicated by [index] in RSS Feed of [name].
 (abbreviation=editFF:)
\'removeFeedFilter: [name]; [index];\'\tRemove Feed Filter indicated by [index] in RSS Feed of [name].
 (abbreviation=removeFF:)
\'setTwitterQuery: [query]; ([users];)\'\tSet [query] with Default Settings. If set [users], notify only from these users.
 (abbreviation=setTQ:)
\'editTwitterQuery: [index]; [query]; ([users];)\'\tEdit Twitter Query indicated by [index].
 (abbreviation=editTQ:)
\'addUserTwitterQuery: [index]; [users];\'\tAdd User to Twitter Query indicated by [index]. That query notify only from these users.
 (abbreviation=addUserTQ:)
\'removeTwitterQuery: [index];\'\tRemove Twitter Query indicated by [index].
 (abbreviation=removeTQ:)

\'help:\'\tShow this Message.

Target:
\tgithub
\tgist
\tgithub_code
\tgitlab
\tgitlab_snippet (Use RE match)
\tgoogle_custom
\tpastebin (Use RE match)
\trss_feed
\ttwitter\n```'''
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@listen_to('How are you?')
def reaction(message):
  isername=message._client.login_data['self']['name'],
  message.send('I\'m fine, thank you.')
