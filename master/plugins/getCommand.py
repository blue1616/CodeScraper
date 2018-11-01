# -*- coding: utf-8 -*-
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re
from . import edit_conf as ec
import os.path
import requests

targets = [
  'github',
  'github_code',
  'gist',
  'gitlab',
  'gitlab_snippet',
  'pastebin',
  'google_custom',
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
#    print(word)
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
    if params.strip().isdigit():
      index = int(params.strip())
      ret = ec.enableKeywordSetting(target, index, False)
      if ret == None:
        post_data = 'No Data'
      else:
        post_data = '`{keyword}` is disabled in _{target}_'.format(keyword=ret, target=target)
    else:
      post_data = 'Please Put Index of the Word'
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
  target = 'github'
  enabled = getEnabledTargets()
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled:
    params = params.split(';')[0]
    if params.strip().isdigit():
      index = int(params.strip())
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
  target = 'github'
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
          valid_num = [1, 2]
          if int(words[1].strip()) in valid_num:
            ret = ec.setSearchLevel(target, index, int(words[1].strip()))
            if ret == '':
              post_data = 'No Data'
            else:
              post_data = 'Set `{keyword}` Search Level to {level}'.format(keyword=ret, level=words[1].strip())
          else:
            post_data = 'Invalid Search Level'
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
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  words = params.strip().split(';')
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
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  if target in enabled:
    words = params.strip().split(';')
    if words[0].strip().isdigit():
      index = int(words[0].strip())
      if len(words) > 1:
        readfile = open(channelfile, 'r')
        channels = []
        for line in readfile.readlines():
          if line.strip() != '':
            channels.append(line.strip())
        readfile.close()
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
        candidatelist = ec.getEnableKeywordlist(g)
        if len(candidatelist.keys()) != 0:
          post_data += '-- Enabled Search Keyword in _{target}_ --\n'.format(target=g)
          for k,v in sorted(candidatelist.items(), key=lambda x: x[1]):
            post_data += str(v) + ' : `' + k + '`\n'
  else:
    post_data = 'Invalid Target'
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
        candidatelist = ec.getKeywordlist(g)
        if len(candidatelist.keys()) != 0:
          post_data += '-- Enabled Search Keyword in _{target}_ --\n'.format(target=g)
          for k,v in sorted(candidatelist.items(), key=lambda x: x[1]):
            post_data += str(v) + ' : `' + k + '`\n'
  else:
    post_data = 'Invalid Target'
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@respond_to('getSearchSetting: (.*)')
@respond_to('getSS: (.*)')
def getKeywordSetting(message, params):
  post_data = ''
  for t in targets:
    if params.strip().startswith(t + ';'):
      target = t
      params = params.replace(t + ';', '', 1)
      break
  params = params.split(';')[0]
  enabled = getEnabledTargets()
  if target in enabled:
    if params.strip().isdigit():
      index = int(params.strip())
      (config, keyword) = ec.getKeywordSetting(target, index)
      if keyword == '':
        post_data = 'No Data'
      else:
        conf_params = [
          'Index',
          'Enable',
          'SearchLevel',
          'Time_Range',
          'Expire_date',
          'Exclude_list',
          'Channel'
        ]
        post_data = 'Settings of `' + keyword + '` is :\n```'
        for p in conf_params:
          if p in config.keys():
            v = config[p]
            if p == 'Exclude_list':
              if len(v) > 20:
                v = ' , '.join(v[0:10]) + ' , ... , ' + ' , '.join(v[-10:-1])
              else:
                v = ' , '.join(v)
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
            raw_result = requests.get(word)
            if raw_result.status_code == 200:
              patt = re.compile(key, re.IGNORECASE)
              if re.search(patt, raw_result.text):
                post_data += 'The pattern, `{keyword}` match to contents of {url}'.format(keyword=key, url=word)
              else:
                post_data += 'The pattern, `{keyword}` not match to contents of {url}'.format(keyword=key, url=word)
            else:
              post_data += 'I couldn\'t access to {url}'.format(url=word)
          else:
            patt = re.compile(key, re.IGNORECASE)
            if re.search(patt, word):
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

@respond_to('help:')
def getAllKeyword(message):
#  candidatelist = setting.getKeywordlist()
  post_data = '''```Command Format is Following:
\t{Command}: {target}; {arg1}; {arg2}; ...

Command List:

\'setKeyword: target; [word]\'\tAdd [word] as New Search Keyword with Default Settings.
 (abbreviation=setK:)
\'enableKeyword: target; [index]\'\tEnable the Search Keyword indicated by [index].
 (abbreviation=enableK:)
\'disableKeyword: target; [index]\'\tDisable the Search Keyword indicated by [index].
 (abbreviation=disableK:)
\'setSearchLevel: target; [index]\'\tSet Search Level of Github Search (1:easily 2:) indicated by [index]. It is used in github and github_code.
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
\'help:\'\tShow this Message.

Target:
\tgithub
\tgist
\tgithub_code
\tgitlab
\tgitlab_snippet (Use RE match)
\tgoogle_custom
\tpastebin (Use RE match)\n```'''
  ret = message._client.webapi.chat.post_message(
    message._body['channel'],
    post_data,
    as_user=True,
    )

@listen_to('How are you?')
def reaction(message):
  isername=message._client.login_data['self']['name'],
  message.send('I\'m fine, thank you.')
