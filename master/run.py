# -*- coding: utf-8 -*-

import argparse
from crontab import CronTab
import datetime
import logging
from logging import getLogger, StreamHandler, Formatter
from multiprocessing import Pool
import math
import os.path
import sys
import time
import traceback
from slackbot.bot import Bot
import master_post as master
import search_api
import slackbot_settings
import plugins.edit_conf_db as ec

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./log/run.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - line %(lineno)d - %(name)s - %(filename)s - \n*** %(message)s')
fh.setFormatter(formatter)

def doSpecialAct(target, channel, key, result):
  if target == 'github':
    pass
  elif target == 'gist':
    pass
  elif target == 'github_code':
    pass
  elif target == 'gitlab':
    pass
  elif target == 'gitlab_snippet':
    pass
  elif target == 'google_custom':
    pass
  elif target == 'pastebin':
    pass
  elif target == 'twitter':
    pass

def getSpecialChannel():
  try:
    channel = slackbot_settings.special_action_channel
    if type(channel) != list:
      return []
    else:
      return channel
  except:
    return []

def runSearchGithub():
  try:
    logger.info('--START GITHUB SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    target = 'github'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        channel = key['Channel']
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        if now < limittime:
          oldtime = now - datetime.timedelta(key['Time_Range'])
          oldday = oldtime.strftime('%Y-%m-%d')
          (results, statuscode) = search_api.searchGithub(key['KEY'], oldday, key['SearchLevel'])
          result = list(set(results) - set(key['Exclude_list']))
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['KEY'] + '` failed to search in _github_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Github_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            ec.setSafetyCount(target, 0)
            if result != []:
              if channel in getSpecialChannel():
                doSpecialAct(target, channel, key['KEY'], result)
              master.postNewPoCFound(key['KEY'], result, channel)
              logger.info('keyword : ' + key['KEY'])
              logger.info('\n'.join(result))
              exclude = results
              ec.clearExcludeList(target, key['Index'])
              ec.addExcludeList(target, key['Index'], exclude)
          time.sleep(10)
        else:
          postdata = '`' + key['KEY'] + '` expired in _github_, and was disabled.'
          logger.info(postdata)
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting(target, key['Index'], False)
  except:
    logger.error('--ERROR HAS OCCURED IN GITHUB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runSearchGithubCode():
  try:
    logger.info('--START GITHUB CODE SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    api_key = slackbot_settings.github_access_token

    target = 'github_code'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        channel = key['Channel']
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        if now < limittime:
          (results, statuscode) = search_api.searchGithubCode(key['KEY'], key['SearchLevel'], api_key)
          result = list(set(results) - set(key['Exclude_list']))
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount('github_code', error_safety)
            postdata = '`' + key['KEY'] + '` failed to search in _github_code_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Github Code_ Module is disabled for safety'
              ec.disable('github_code')
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            ec.setSafetyCount('github_code', 0)
            if key['__INITIAL__'] == True:
              ec.haveSearched(target, key['Index'])
            if result != []:
              postdata = 'New Code Found about `' + key['KEY'] + '` in _github_code_'
              master.postAnyData(postdata, channel)
              if key['__INITIAL__'] == True:
                master.postAnyData(result[0], channel)
              else:
                if channel in getSpecialChannel():
                  doSpecialAct(target, channel, key['KEY'], result)
                master.postAnyData('\n'.join(result), channel)
              logger.info('keyword : ' + key['KEY'])
              logger.info('\n'.join(result))
              exclude = results
#              ec.clearExcludeList('github_code', conf['Index'])
              ec.addExcludeList('github_code', key['Index'], exclude)
          time.sleep(10)
        else:
          postdata = '`' + key['KEY'] + '` expired in _github_code_, and was disabled.'
          logger.info(postdata)
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting('github_code', key['Index'], False)
  except:
    logger.error('--ERROR HAS OCCURED IN GITHUB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runSearchGist():
  try:
    logger.info('--START GIST SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    target = 'gist'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        channel = key['Channel']
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        if now < limittime:
          oldtime = now - datetime.timedelta(key['Time_Range'])
          oldday = oldtime.strftime('%Y-%m-%d')
          (results, statuscode) = search_api.searchGist(key['KEY'], oldday)
          result = list(set(results) - set(key['Exclude_list']))
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['KEY'] + '` failed to search in _gist_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Gist_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            ec.setSafetyCount(target, 0)
            if result != []:
              if channel in getSpecialChannel():
                doSpecialAct(target, channel, key['KEY'], result)
              postdata = 'New Code Found about `' + key['KEY'] + '` in _gist_'
              master.postAnyData(postdata, channel)
              master.postAnyData('\n'.join(result), channel)
              logger.info('keyword : ' + key['KEY'])
              logger.info('\n'.join(result))
              exclude = results
              ec.clearExcludeList(target, key['Index'])
              ec.addExcludeList(target, key['Index'], exclude)
          time.sleep(45)
        else:
          postdata = '`' + key['KEY'] + '` is expired in _gist_, and disabled.'
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting(target, key['Index'], False)
          logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GIST SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runSearchGitlab():
  try:
    logger.info('--START GITLAB SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    target = 'gitlab'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        channel = key['Channel']
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        if now < limittime:
          (results, statuscode) = search_api.searchGitlab(key['KEY'])
          result = list(set(results) - set(key['Exclude_list']))
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['KEY'] + '` failed to search in _gitlab_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Gitlab_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            if error_safety != 0:
              ec.setSafetyCount(target, 0)
            if key['__INITIAL__'] == True:
              ec.haveSearched(target, key['Index'])
            if result != []:
              postdata = 'New Code Found about `' + key['KEY'] + '` in _gitlab_'
              master.postAnyData(postdata, channel)
              url = []
              for i in result:
                url.append('https://gitlab.com' + i)
              if key['__INITIAL__'] == True:
                master.postAnyData(url[0], channel)
              else:
                if channel in getSpecialChannel():
                  doSpecialAct(target, channel, key['KEY'], url)
                master.postAnyData('\n'.join(url), channel)
              logger.info('keyword : ' + key['KEY'])
              logger.info('\n'.join(url))
              exclude = results
              ec.clearExcludeList(target, key['Index'])
              ec.addExcludeList(target, key['Index'], exclude)
          time.sleep(30)
        else:
          postdata = '`' + key['KEY'] + '` is expired in _gitlab_, and disabled.'
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting(target, key['Index'], False)
          logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GITLAB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runSearchGitlabSnippets():
  try:
    logger.info('--START GITLAB SNIPPETS SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    target = 'gitlab_snippet'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        channel = key['Channel']
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        if now > limittime:
          postdata = '`' + key['KEY'] + '` is expired in _gitlab_snippet_, and disabled.'
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting('gitlab_snippet', key['Index'], False)
          logger.info(postdata)
      keywords = ec.getEnableKeywords(target)
      if keywords != None and keywords != []:
        keylist = [d.get('KEY') for d in keywords]
        (results, statuscode) = search_api.searchGitlabSnippets(keylist)
        if statuscode != 200:
          error_safety += 1
          ec.setSafetyCount(target, error_safety)
          postdata = '_gitlab_snippet_ failed to search.\nStatus Code: ' + str(statuscode)
          master.postAnyData(postdata, channel)
          logger.info(postdata)
          if error_safety > safe_limit:
            postdata = 'Too Many Errors. _Gitlab Snippet_ Module is disabled for safety'
            ec.disable(target)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
        else:
          ec.setSafetyCount(target, 0)
          for key in keywords:
            if key['KEY'] in results.keys():
              result = list(set(results[key['KEY']]) - set(key['Exclude_list']))
              if result != []:
                channel = key['Channel']
                postdata = 'New Code Found about `' + key['KEY'] + '` in _gitlab_snippet_'
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                url = []
                for i in result:
                  url.append('https://gitlab.com' + i)
                  logger.info('https://gitlab.com' + i)
#                exclude = list(set(results[word]) & set(keywords[word][1]))
                exclude = results[key['KEY']]
                if channel in getSpecialChannel():
                  doSpecialAct(target, channel, key['KEY'], url)
                master.postAnyData('\n'.join(url), channel)
                ec.clearExcludeList(target, key['Index'])
                ec.addExcludeList(target, key['Index'], exclude)
  except:
    logger.error('--ERROR HAS OCCURED IN GITLAB SNIPPETS SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runSearchPastebin():
  logger.info('--START PASTEBIN SEARCH--')
  while True:
    try:
      now = datetime.date.today()
      today = now.strftime('%Y-%m-%d')
      target = 'pastebin'
      keywords = ec.getEnableKeywords(target)

      if ec.isEnable(target) and keywords != None and keywords != []:
        safe_limit = 10
        error_safety = ec.getSafetyCount(target)
        for key in keywords:
          channel = key['Channel']
          limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
          if now > limittime:
            postdata = '`' + key['KEY'] + '` is expired in _pastebin_, and disabled.'
            master.postAnyData(postdata, channel)
            ec.enableKeywordSetting(target, key['Index'], False)
            logger.info(postdata)
        keywords = ec.getEnableKeywords(target)
        if keywords != None and keywords != []:
          (pastelist, statuscode) = search_api.getPasteList(100)
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = 'pastebin serach failed in _pastebin_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety == 5:
              postdata = 'Pause to access pastebin'
              master.postAnyData(postdata, channel)
              logger.info(postdata)
              time.sleep(300)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Pastebin_ Module is disabled for safety'
              ec.disable('pastebin')
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            searchedpastes = ec.getSearchedPastes()
            searchlist = {}
            for paste, conf in pastelist.items():
              if not paste in searchedpastes:
                searchlist[paste] = conf
            if len(searchlist.keys()) > 30:
              ec.setSearchedPastes(pastelist.keys())
              logger.info('The number of scraping pastes is ' + str(len(searchlist.keys())))
              keylist = [d.get('KEY') for d in keywords]
              (results, statuscode) = search_api.scrapePastebin(keylist, searchlist)
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount(target, error_safety)
                postdata = 'pastebin serach failed in _pastebin_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Pastebin_ Module is disabled for safety'
                  ec.disable(target)
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                ec.setSafetyCount(target, 0)
                for key in keywords:
                  if key['KEY'] in results.keys():
                    if results[key['KEY']] != []:
                      channel = key['Channel']
                      postdata = 'New Code Found about `' + key['KEY'] + '` in _pastebin_'
                      if channel in getSpecialChannel():
                        doSpecialAct(target, channel, key['KEY'], results[key['KEY']])
                      master.postAnyData(postdata, channel)
                      logger.info(postdata)
                      exclude = results[key['KEY']]
                      master.postAnyData('\n'.join(results[key['KEY']]), channel)
      time.sleep(10)
    except:
      logger.error('--ERROR HAS OCCURED IN PASTEBIN SEARCH--')
      logger.error(traceback.format_exc())
      master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
      time.sleep(10)

def runSearchGoogleCustom():
  try:
    engine_id = slackbot_settings.google_custom_search_engine_id
    api_key = slackbot_settings.google_custom_api_key
    logger.info('--START GOOGLE CUSTOM SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    target = 'google_custom'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)
      for key in keywords:
        limittime = datetime.datetime.strptime(key['Expire_date'], '%Y-%m-%d').date()
        channel = key['Channel']
        if now < limittime:
          (result, statuscode) = search_api.googleCustomSearch(key['KEY'], engine_id, api_key)
          if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['KEY'] + '` failed to search in _google_custom_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Google Custom_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
          else:
            result_post = list(set(result.keys()) - set(key['Exclude_list']))
            ec.setSafetyCount(target, 0)
            if key['__INITIAL__'] == True:
              ec.haveSearched(target, key['Index'])
            if result_post != []:
              postdata = 'New Code Found about `' + key['KEY'] + '` in _google_custom_'
              master.postAnyData(postdata, channel)
              logger.info(postdata)
              if key['__INITIAL__'] == True:
                result_post = result_post[:1]
              for i in result_post:
                logger.info(i)
                post_code = result[i][0] + '\n' + i + '\n'
                if channel in getSpecialChannel():
                  doSpecialAct(target, channel, key['KEY'], post_code)
                master.postAnyData(post_code, channel)
              exclude = list(result.keys())
#                  ec.clearExcludeList('google_custom', conf['Index'])
              ec.addExcludeList(target, key['Index'], exclude)
          time.sleep(30)
        else:
          postdata = '`' + key['KEY'] + '` is expired in _google_custom_, and disabled.'
          master.postAnyData(postdata, channel)
          ec.enableKeywordSetting(target, key['Index'], False)
          logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GOOGLE CUSTOM SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def filterFeeds(feeds, filter):
  filtereditems = []
  for f in feeds:
    matched = True
    for word in filter:
      target = '__ALL__'
      name = word
      pos = word.find('>')
      if pos > 0 and len(word) > pos+1:
        target = word[:pos].strip()
        name = word[pos+1:].strip()
      if name.startswith('!'):
        name = name[1:].strip()
        if target in f.keys():
          if type(f[target]) == list:
            text = ''.join(map(str, f[target]))
          else:
            text = f[target]
          if text.lower().find(name.lower()) > 0:
            matched = False
        else:
          text = ''
          for i in f.keys():
            if type(f[i]) == list:
              text += ''.join(map(str, f[i]))
            else:
              text += f[i]
          if text.lower().find(name.lower()) > 0:
            matched = False
      else:
        if target in f.keys():
          if type(f[target]) == list:
            text = ''.join(map(str,f[target]))
          else:
            text = f[target]
          if text.lower().find(name.lower()) < 0:
            matched = False
        else:
          text = ''
          for i in f.keys():
            if type(f[i]) == list:
              text += ''.join(map(str, f[i]))
            else:
              text += f[i]
          if text.lower().find(name.lower()) < 0:
            matched = False
    if matched:
      filtereditems.append(f)
  return filtereditems

def runRSSFeeds():
  try:
    logger.info('--GET NEW RSS FEEDS--')

    target = 'rss_feed'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)

      for key in keywords:
        channel = key['Channel']
        filter = key['Filters']
        url = key['URL']
        lastpost = key['Last_Post']
        initialstate = key['__INITIAL__']
        (result, statuscode) = search_api.getRSSFeeds(url, lastpost)
        if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['Name'] + '` failed to get _RSS_Feeds_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _RSS_Feeds_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
        else:
          if error_safety != 0:
            ec.setSafetyCount(target, 0)
          if len(result) > 0:
            if initialstate:
              result = result[:1]
              ec.haveSearched(target, key['Name'])
            filteredfeeds = {}
            if filter != []:
              for f in filter:
                c = f['Channel']
                w = f['Words']
                ff = filterFeeds(result, w)
                if ff != []:
                  if c in filteredfeeds.keys():
                    filteredfeeds[c] += ff
                  else:
                    filteredfeeds[c] = ff
            else:
              if result != {}:
                filteredfeeds[channel] = result
            lastpost = {'title':result[0]['title'], 'link':result[0]['link'], 'timestamp':result[0]['timestamp']}
            ec.setRSSLastPost(key['Name'], lastpost)
            if filteredfeeds != {}:
              for c, feeds in filteredfeeds.items():
                if c in getSpecialChannel():
                  doSpecialAct(target, c, key['Name'], feeds)
                postdata = 'New Feed in `' + key['Name'] + '`'
                master.postAnyData(postdata, c)
                logger.info(postdata)
                postdata = ''
                for f in feeds:
                  postdata = f['title'] + '\n'
                  postdata += f['link']
                  logger.info(postdata)
                  master.postAnyData(postdata, c)
          time.sleep(30)
  except:
    logger.error('--ERROR HAS OCCURED IN GETTING RSS FEEDS--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runTwitterSearch():
  try:
    logger.info('--START TWITTER SEARCH--')

    target = 'twitter'
    keywords = ec.getEnableKeywords(target)

    if ec.isEnable(target) and keywords != None and keywords != []:
      safe_limit = 6
      error_safety = ec.getSafetyCount(target)

      for key in keywords:
        channel = key['Channel']
        query = key['Query']
        users = key['Users']
        lastpost = key['Last_Post']
        initialstate = key['__INITIAL__']
        (result, statuscode) = search_api.getTweets(users, query, lastpost)
        if statuscode != 200:
            error_safety += 1
            ec.setSafetyCount(target, error_safety)
            postdata = '`' + key['Name'] + '` failed to get _Twitter_.\nStatus Code: ' + str(statuscode)
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            if error_safety > safe_limit:
              postdata = 'Too Many Errors. _Twitter_ Module is disabled for safety'
              ec.disable(target)
              master.postAnyData(postdata, channel)
              logger.info(postdata)
        else:
          if error_safety != 0:
            ec.setSafetyCount(target, 0)
          if len(result) > 0:
            if initialstate:
              result = result[:1]
              ec.haveSearched(target, key['Index'])
            lastpost = result[0]
            ec.setTwitterLastPost(key['Index'], lastpost)
            postdata = 'New Tweets in `' + key['KEY'] + '`'
            master.postAnyData(postdata, channel)
            logger.info(postdata)
            postdata = ''
            for tw in result:
              postdata = 'https://twitter.com' + tw['link']
              postdata += ' (FROM: '+ tw['user'] + ')\n'
              postdata += '>>>' + tw['tweet'] + '\n'
              logger.info(postdata)
              if channel in getSpecialChannel():
                doSpecialAct(target, channel, key['KEY'], tw)
              master.postAnyData(postdata, channel)
          time.sleep(30)
  except:
    logger.error('--ERROR HAS OCCURED IN SEARCHING TWITTER--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])

def runBot():
  bot = Bot()
  bot.run()

class JobConfig(object):
  def __init__(self, crontab, job):
    self._crontab = crontab
    self.job = job

  def schedule(self):
    crontab = self._crontab
    return datetime.now() + timedelta(seconds=math.ceil(crontab.next()))

  def next(self):
    crontab = self._crontab
    return math.ceil(crontab.next())

def job_controller(jobConfig):
  while True:
    try:
      time.sleep(jobConfig.next())
      jobConfig.job()
    except KeyboardInterrupt:
      break

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--db-host', type=str, default='localhost', help='DATABASE HOST NAME')
  parser.add_argument('--db-port', type=int, default=27017, help='DATABASE PORT')
  parser.add_argument('--db-name', type=str, default='codescraper-database', help='DATABASE NAME')
  args = parser.parse_args()
  ec.setDB(args.db_host, args.db_port, args.db_name)

  jobConfigs = []

  try:
    slackbot_settings.API_TOKEN
  except NameError:
    sys.exit()
    print('Slackbot API TOKEN is required')

  start_state = []
  runpastebinflag = False

  try:
    channels = slackbot_settings.channels
    if type(channels) != list or channels == []:
      print('Set more than 1 channel')
      sys.exit()

    ec.setUsingChannels(channels)

    if slackbot_settings.enable_github_search:
      default_github = slackbot_settings.github_default_settings
      ret = ec.setDefaultSettings('github', default_github)
      if ret:
        github_interval = slackbot_settings.github_search_interval
        jobConfigs.append(JobConfig(CronTab(github_interval), runSearchGithub))
        message = 'Started'
        start_state.append(('github', 'SUCCESS', message))
      else:
        ec.disable('github')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('github', 'FAILED', message))
    else:
      ec.disable('github')

    if slackbot_settings.enable_github_code_search:
      default_github_code = slackbot_settings.github_code_default_settings
      ret = ec.setDefaultSettings('github_code', default_github_code)
      if ret:
        gist_interval = slackbot_settings.github_code_search_interval
        jobConfigs.append(JobConfig(CronTab(gist_interval), runSearchGithubCode))
        message = 'Started'
        start_state.append(('github_code', 'SUCCESS', message))
      else:
        ec.disable('github_code')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('github_code', 'FAILED', message))
    else:
      ec.disable('github_code')

    if slackbot_settings.enable_gist_search:
      default_gist = slackbot_settings.gist_default_settings
      ret = ec.setDefaultSettings('gist', default_gist)
      if ret:
        gist_interval = slackbot_settings.gist_search_interval
        jobConfigs.append(JobConfig(CronTab(gist_interval), runSearchGist))
        message = 'Started'
        start_state.append(('gist', 'SUCCESS', message))
      else:
        ec.disable('gist')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('gist', 'FAILED', message))
    else:
      ec.disable('gist')

    if slackbot_settings.enable_gitlab_search:
      default_gitlab = slackbot_settings.gitlab_default_settings
      ret = ec.setDefaultSettings('gitlab', default_gitlab)
      if ret:
        gitlab_interval = slackbot_settings.gitlab_search_interval
        jobConfigs.append(JobConfig(CronTab(gitlab_interval), runSearchGitlab))
        message = 'Started'
        start_state.append(('gitlab', 'SUCCESS', message))
      else:
        ec.disable('gitlab')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('gitlab', 'FAILED', message))
    else:
      ec.disable('gitlab')

    if slackbot_settings.enable_gitlab_snippet_search:
      default_gitlab_snippet = slackbot_settings.gitlab_snippet_default_settings
      ret = ec.setDefaultSettings('gitlab_snippet', default_gitlab_snippet)
      if ret:
        gitlab_snippet_interval = slackbot_settings.gitlab_snippet_search_interval
        jobConfigs.append(JobConfig(CronTab(gitlab_snippet_interval), runSearchGitlabSnippets))
        message = 'Started'
        start_state.append(('gitlab_snippet', 'SUCCESS', message))
      else:
        ec.disable('gitlab_snippet')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('gitlab_snippet', 'FAILED', message))
    else:
      ec.disable('gitlab_snippet')

    if slackbot_settings.enable_pastebin_search:
      default_pastebin = slackbot_settings.pastebin_default_settings
      ret = ec.setDefaultSettings('pastebin', default_pastebin)
      if ret:
        runpastebinflag = True
        message = 'Started'
        start_state.append(('pastebin', 'SUCCESS', message))
      else:
        ec.disable('pastebin')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('pastebin', 'FAILED', message))
    else:
      ec.disable('pastebin')

    if slackbot_settings.enable_google_custom_search:
      slackbot_settings.google_custom_search_engine_id
      slackbot_settings.google_custom_api_key
      default_google_custom = slackbot_settings.google_custom_default_settings
      ret = ec.setDefaultSettings('google_custom', default_google_custom)
      if ret:
        google_custom_interval = slackbot_settings.google_custom_search_interval
        jobConfigs.append(JobConfig(CronTab(google_custom_interval), runSearchGoogleCustom))
        message = 'Started'
        start_state.append(('google_custom', 'SUCCESS', message))
      else:
        ec.disable('google_custom')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('google_custom', 'FAILED', message))
    else:
      ec.disable('google_custom')

    if slackbot_settings.enable_rss_feed:
      default_channel = slackbot_settings.rss_feed_default_channel
      ret = ec.setDefaultSettings('rss_feed', {'Channel':default_channel})
      if ret:
        rss_interval = slackbot_settings.rss_feed_interval
        jobConfigs.append(JobConfig(CronTab(rss_interval), runRSSFeeds))
        message = 'Started'
        start_state.append(('rss_feed', 'SUCCESS', message))
      else:
        ec.disable('rss_feed')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('rss_feed', 'FAILED', message))
    else:
      ec.disable('rss_feed')

    if slackbot_settings.enable_twitter:
      default_channel = slackbot_settings.twitter_default_channel
      ret = ec.setDefaultSettings('twitter', {'Channel':default_channel})
      if ret:
        twitter_interval = slackbot_settings.twitter_interval
        jobConfigs.append(JobConfig(CronTab(twitter_interval), runTwitterSearch))
        message = 'Started'
        start_state.append(('twitter', 'SUCCESS', message))
      else:
        ec.disable('twitter')
        message = 'Default Setting is wrong. Disabled'
        start_state.append(('twitter', 'FAILED', message))
    else:
      ec.disable('twitter')

  except AttributeError:
    print('slackbot_settings is something wrong')
    sys.exit(0)

  postdata = '---CodeScraper Slackbot Started---\n```'
  for m in start_state:
    postdata += ' : '.join(m) + '\n'
  postdata += '```'
  master.postAnyData(postdata, channels[0])
  print(postdata)

  if runpastebinflag:
    p = Pool(len(jobConfigs) + 2)
  else:
    p = Pool(len(jobConfigs) + 1)
  try:
    p.apply_async(runBot)
    if runpastebinflag:
      p.apply_async(runSearchPastebin)
    p.map(job_controller, jobConfigs)
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  main()
