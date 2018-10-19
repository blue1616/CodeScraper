import json
import datetime
import shutil
import time
import re
import os.path

base = os.path.dirname(os.path.abspath(__file__))
confjson = os.path.normpath(os.path.join(base, '../settings/searchCandidate.json'))
channelfile = os.path.normpath(os.path.join(base, '../settings/channellist'))

modules = [
  'github',
  'gist',
  'github_code',
  'gitlab',
  'gitlab_snippet',
  'google_custom',
  'pastebin'
]

github_settings = {
  'Enable':False,
  'SearchLevel':1,
  'Time_Range':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

gist_settings = {
  'Enable':False,
  'Time_Range':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

github_code_settings = {
  'Enable':False,
  'SearchLevel':1,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

gitlab_settings = {
  'Enable':False,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

gitlab_snippet_settings = {
  'Enable':False,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

pastebin_settings = {
  'Enable':False,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

google_custom_settings = {
  'Enable':False,
  'Expire_date':1,
  'Exclude_list':[],
  'Channel':'None'
}

setting_set = {
  'github':github_settings,
  'gist':gist_settings,
  'github_code':github_code_settings,
  'gitlab':gitlab_settings,
  'gitlab_snippet':gitlab_snippet_settings,
  'google_custom':google_custom_settings,
  'pastebin':pastebin_settings
}

def isEnable(target):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r')
    searchconf = json.load(conffile)
    if keyword in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf[keyword].keys() and searchconf[keyword]['__DEFAULT_SETTING__']['Index'] == 0:
      enable = True
    else:
      enable = False
    conffile.close()
    return enable
  else:
    return None

def getAllState():
  result = {}
  conffile = open(confjson, 'r')
  searchconf = json.load(conffile)
  conffile.close()
  for m in modules:
    keyword = 'keyword_' + m
    if keyword in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf[keyword].keys() and searchconf[keyword]['__DEFAULT_SETTING__']['Index'] == 0:
      enable = True
    else:
      enable = False
    result[m] = enable
  return result

def disable(target):
  if target in modules:
    keyword = 'keyword_' + target
    if os.path.exists(confjson):
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
    else:
      conffile = open(confjson, 'w')
      searchconf = {keyword:{}}
    default_setting = setting_set[target]
    default_setting['Index'] = -1
    if keyword in searchconf.keys():
      searchconf[keyword]['__DEFAULT_SETTING__'] = default_setting
    else:
      searchconf[keyword] = {}
      searchconf[keyword]['__DEFAULT_SETTING__'] = default_setting
    conffile.seek(0)
    conffile.write(json.dumps(searchconf, indent=2))
    conffile.truncate()
    conffile.close()
    return True
  else:
    return None

def setDefaultSettings(target, default_dict, channels):
  if target in modules:
    keyword = 'keyword_' + target
    required = {
      'Enable':bool,
      'SearchLevel':int,
      'Time_Range':int,
      'Expire_date':int,
      'Exclude_list':list,
      'Channel':str
    }
    setter = setting_set[target]
    for k in setter.keys():
      if not k in default_dict.keys() and type(default_dict[k]) == required[k]:
        return False
      if k == 'SearchLevel':
        if not default_dict['SearchLevel'] in [1,2]:
          return False
    if not default_dict['Channel'] in channels:
      default_dict['Channel'] = channels[0]
    if os.path.exists(confjson):
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
    else:
      conffile = open(confjson, 'w')
      searchconf = {keyword:{}}
    for k in setter.keys():
      setter[k] = default_dict[k]
    setter['Index'] = 0
    if keyword in searchconf.keys():
      searchconf[keyword]['__DEFAULT_SETTING__'] = setter
    else:
      searchconf[keyword] = {}
      searchconf[keyword]['__DEFAULT_SETTING__'] = setter
    conffile.seek(0)
    conffile.write(json.dumps(searchconf, indent=2))
    conffile.truncate()
    conffile.close()
    return True
  else:
    return None

def backupConfig():
  now = datetime.datetime.now()
  timestamp = now.strftime('%Y%m%d%H%M%S')
  backupfile = confjson + '-' + timestamp
  shutil.copyfile(confjson, backupfile)
  time.sleep(3)

def setNewCandidate(target, word):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r+')
    searchconf = json.load(conffile)
    ret = 0
    if keyword in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf[keyword].keys():
      default = searchconf[keyword]['__DEFAULT_SETTING__']
      setter = setting_set[target]
      for k in setter.keys():
        if k == 'Expire_date':
          today = datetime.date.today()
          limit = (today + datetime.timedelta(int(default['Expire_date']))).strftime('%Y-%m-%d')
          setter[k] = limit
        else:
          setter[k] = default[k]
      if word in searchconf[keyword].keys():
        setter['Index'] = searchconf[keyword][word]['Index']
        searchconf[keyword][word] = setter
        ret = searchconf[keyword][word]['Index'] * -1
      else:
        index = 0
        for key, conf in searchconf[keyword].items():
          if index < conf['Index']:
            index = conf['Index']
        index += 1
        setter['Index'] = index
        searchconf[keyword][word] = setter
        ret = index
      conffile.seek(0)
      conffile.write(json.dumps(searchconf, indent=2))
      conffile.truncate()
    conffile.close()
    return ret
  else:
    return None

def enableCandidateSetting(target, index, enable):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r+')
    searchconf = json.load(conffile)
    setter = setting_set[target]
    eword = None
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        if index == conf['Index']:
          eword = key
          setter = conf
          break
      setter['Enable'] = enable
      searchconf[keyword][key] = setter
      conffile.seek(0)
      conffile.write(json.dumps(searchconf, indent=2))
      conffile.truncate()
    conffile.close()
    return eword
  else:
    None

def setSearchLevel(target, index, level):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    word = ''
    if 'SearchLevel' in setter.keys():
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
      if keyword in searchconf.keys():
        for key, conf in searchconf[keyword].items():
          if index == conf['Index']:
            word = key
            setter = conf
            break
        setter['SearchLevel'] = level
        searchconf[keyword][key] = setter
        conffile.seek(0)
        conffile.write(json.dumps(searchconf, indent=2))
        conffile.truncate()
      conffile.close()
      return word
    else:
      None
  else:
    return None

def setSearchRange(target, index, days):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    word = ''
    if 'Time_Range' in setter.keys():
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
      if keyword in searchconf.keys():
        for key, conf in searchconf[keyword].items():
          if index == conf['Index']:
            word = key
            setter = conf
            break
        setter['Time_Range'] = days
        searchconf[keyword][key] = setter
        conffile.seek(0)
        conffile.write(json.dumps(searchconf, indent=2))
        conffile.truncate()
      conffile.close()
      return word
    else:
      return None
  else:
    return None

def setExpireDate(target, index, limit):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    conffile = open(confjson, 'r+')
    searchconf = json.load(conffile)
    regx = '\d{4}-(0[0-9]|1[0-2])-([0-2][0-9]|3[01])'
    word = ''
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        if index == conf['Index']:
          word = key
          setter = conf
          break
      if re.match(regx, limit):
        setter['Expire_date'] = limit
      searchconf[keyword][key] = setter
      conffile.seek(0)
      conffile.write(json.dumps(searchconf, indent=2))
      conffile.truncate()
    conffile.close()
    return word
  else:
    return None

def setChannel(target, index, channel):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    conffile = open(confjson, 'r+')
    searchconf = json.load(conffile)
    readfile = open(channelfile, 'r')
    channels = []
    for line in readfile.readlines():
      if line.strip() != '':
        channels.append(line.strip())
    readfile.close()
    word = ''
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        if index == conf['Index']:
          word = key
          setter = conf
          break
      if channel in channels:
        setter['Channel'] = channel
      searchconf[keyword][key] = setter
      conffile.seek(0)
      conffile.write(json.dumps(searchconf, indent=2))
      conffile.truncate()
    conffile.close()
    return word
  else:
    None

def addExcludeList(target, index, exclude):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    if 'Exclude_list' in setter.keys():
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
      word = ''
      if keyword in searchconf.keys():
        for key, conf in searchconf[keyword].items():
          if index == conf['Index']:
            word = key
            setter = conf
            break
        setter['Exclude_list'].extend(exclude)
        searchconf[keyword][key] = setter
        conffile.seek(0)
        conffile.write(json.dumps(searchconf, indent=2))
        conffile.truncate()
      conffile.close()
      return word
    else:
      None
  else:
    None

def clearExcludeList(target, index):
  if target in modules:
    keyword = 'keyword_' + target
    setter = setting_set[target]
    if 'Exclude_list' in setter.keys():
      conffile = open(confjson, 'r+')
      searchconf = json.load(conffile)
      word = ''
      if keyword in searchconf.keys():
        for key, conf in searchconf[keyword].items():
          if index == conf['Index']:
            word = key
            setter = conf
            break
        setter['Exclude_list'] = []
        searchconf[keyword][key] = setter
        conffile.seek(0)
        conffile.write(json.dumps(searchconf, indent=2))
        conffile.truncate()
      conffile.close()
      return word
    else:
      return None
  else:
    return None

def getCandidatelist(target):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r')
    searchconf = json.load(conffile)
    alllist = {}
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        alllist[key] = conf['Index']
    conffile.close()
    return alllist
  return None

def getEnableCandidatelist(target):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r')
    searchconf = json.load(conffile)
    enablelist = {}
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        if conf['Enable'] == True:
          enablelist[key] = conf['Index']
    conffile.close()
    return enablelist
  else:
    return None

def getCandidateSetting(target, index):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r')
    searchconf = json.load(conffile)
    config = {}
    word = ''
    if keyword in searchconf.keys():
      for key, conf in searchconf[keyword].items():
        if index == conf['Index']:
          config = conf
          word = key
          break
    conffile.close()
    return config, word
  else:
    return None

def setSafetyCount(target, count):
  if target in modules:
    keyword = 'keyword_' + target
    conffile = open(confjson, 'r+')
    searchconf = json.load(conffile)
    if keyword in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf[keyword].keys():
      searchconf[keyword]['__DEFAULT_SETTING__']['__SAFETY__'] = count
    else:
      conffile.close()
      return False
    conffile.seek(0)
    conffile.write(json.dumps(searchconf, indent=2))
    conffile.truncate()
    conffile.close()
    return True
  else:
    return None
