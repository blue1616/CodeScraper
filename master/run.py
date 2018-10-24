# -*- coding: utf-8 -*-

from slackbot.bot import Bot
import logging
from logging import getLogger, StreamHandler, Formatter
from crontab import CronTab
import datetime
import time
import json
import master_post as master
import os.path
from multiprocessing import Pool
import math
import search_api
import slackbot_settings
import plugins.edit_conf as ec
import traceback
import sys

base = os.path.dirname(os.path.abspath(__file__))
configfile = os.path.normpath(os.path.join(base, './settings/searchKeyword.json'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./log/run.log')
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - line %(lineno)d - %(name)s - %(filename)s - \n*** %(message)s')
fh.setFormatter(formatter)

def runSearchGithub():
  try:
    logger.info('--START GITHUB SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()

    if 'keyword_github' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_github'].keys() and searchconf['keyword_github']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_github']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_github']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_github'].items():
        if conf['Index'] != 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              oldtime = now - datetime.timedelta(conf['Time_Range'])
              oldday = oldtime.strftime('%Y-%m-%d')
              (results, statuscode) = search_api.searchGithub(key, oldday, conf['SearchLevel'])
              result = list(set(results) - set(conf['Exclude_list']))
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount('github', error_safety)
                postdata = '`' + key + '` failed to search in _github_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Github_ Module is disabled for safety'
                  ec.disable('github')
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                if error_safety != 0:
                  ec.setSafetyCount('github', 0)
                if result != []:
                  master.postNewPoCFound(key, result, channel)
                  logger.info('keyword : ' + key)
                  logger.info('\n'.join(result))
                  exclude = results
                  ec.clearExcludeList('github', conf['Index'])
                  ec.addExcludeList('github', conf['Index'], exclude)
              time.sleep(10)
            else:
              postdata = '`' + key + '` expired in _github_, and was disabled.'
              logger.info(postdata)
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('github', conf['Index'], False)
  except:
    logger.error('--ERROR HAS OCCURED IN GITHUB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('github', conf['Index'], False)

def runSearchGithubCode():
  try:
    logger.info('--START GITHUB CODE SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')
#    print(today)

    api_key = slackbot_settings.github_access_token
    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()

    if 'keyword_github_code' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_github_code'].keys() and searchconf['keyword_github_code']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_github_code']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_github_code']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_github_code'].items():
        if conf['Index'] > 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              (results, statuscode) = search_api.searchGithubCode(key, conf['SearchLevel'], api_key)
              result = list(set(results) - set(conf['Exclude_list']))
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount('github_code', error_safety)
                postdata = '`' + key + '` failed to search in _github_code_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Github Code_ Module is disabled for safety'
                  ec.disable('github_code')
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                if error_safety != 0:
                  ec.setSafetyCount('github_code', 0)
                if result != []:
                  postdata = 'New Code Found about `' + key + '` in _github_code_'
                  master.postAnyData(postdata, channel)
                  master.postAnyData('\n'.join(result), channel)
                  logger.info('keyword : ' + key)
                  logger.info('\n'.join(result))
                  exclude = results
                  ec.clearExcludeList('github_code', conf['Index'])
                  ec.addExcludeList('github_code', conf['Index'], exclude)
              time.sleep(10)
            else:
              postdata = '`' + key + '` expired in _github_code_, and was disabled.'
              logger.info(postdata)
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('github_code', conf['Index'], False)
  except:
    logger.error('--ERROR HAS OCCURED IN GITHUB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('github', conf['Index'], False)

def runSearchGist():
  try:
    logger.info('--START GIST SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()

    if 'keyword_gist' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_gist'].keys() and searchconf['keyword_gist']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_gist']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_gist']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_gist'].items():
        if conf['Index'] > 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              oldtime = now - datetime.timedelta(conf['Time_Range'])
              oldday = oldtime.strftime('%Y-%m-%d')
              (results, statuscode) = search_api.searchGist(key, oldday)
              result = list(set(results) - set(conf['Exclude_list']))
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount('gist', error_safety)
                postdata = '`' + key + '` failed to search in _gist_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Gist_ Module is disabled for safety'
                  ec.disable('gist')
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                if error_safety != 0:
                  ec.setSafetyCount('gist', 0)
                if result != []:
                  postdata = 'New Code Found about `' + key + '` in _gist_'
                  master.postAnyData(postdata, channel)
                  master.postAnyData('\n'.join(result), channel)
                  logger.info('keyword : ' + key)
                  logger.info('\n'.join(result))
                  exclude = results
                  ec.clearExcludeList('gist', conf['Index'])
                  ec.addExcludeList('gist', conf['Index'], exclude)
              time.sleep(45)
            else:
              postdata = '`' + key + '` is expired in _gist_, and disabled.'
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('gist', conf['Index'], False)
              logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GIST SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('gist', conf['Index'], False)

def runSearchGitlab():
  try:
    logger.info('--START GITLAB SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()

    if 'keyword_gitlab' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_gitlab'].keys() and searchconf['keyword_gitlab']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_gitlab']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_gitlab']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_gitlab'].items():
        if conf['Index'] > 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              (results, statuscode) = search_api.searchGitlab(key)
              result = list(set(results) - set(conf['Exclude_list']))
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount('gitlab', error_safety)
                postdata = '`' + key + '` failed to search in _gitlab_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Gitlab_ Module is disabled for safety'
                  ec.disable('gitlab')
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                if error_safety != 0:
                  ec.setSafetyCount('gitlab', 0)
                if result != []:
                  postdata = 'New Code Found about `' + key + '` in _gitlab_'
                  master.postAnyData(postdata, channel)
                  url = []
                  for i in result:
                    url.append('https://gitlab.com' + i)
                  master.postAnyData('\n'.join(url), channel)
                  logger.info('keyword : ' + key)
                  logger.info('\n'.join(url))
                  exclude = results
                  ec.clearExcludeList('gitlab', conf['Index'])
                  ec.addExcludeList('gitlab', conf['Index'], exclude)
              time.sleep(30)
            else:
              postdata = '`' + key + '` is expired in _gitlab_, and disabled.'
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('gitlab', conf['Index'], False)
              logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GITLAB SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('gitlab', conf[0], False)

def runSearchGitlabSnippets():
  try:
    logger.info('--START GITLAB SNIPPETS SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')
    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()
    keywords = {}
    channel = ''

    if 'keyword_gitlab_snippet' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_gitlab_snippet'].keys() and searchconf['keyword_gitlab_snippet']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_gitlab_snippet']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_gitlab_snippet']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_gitlab_snippet'].items():
        if conf['Index'] > 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              keywords[key] = (conf['Index'], conf['Exclude_list'])
            else:
              postdata = '`' + key + '` is expired in _gitlab_snippet_, and disabled.'
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('gitlab_snippet', conf['Index'], False)
              logger.info(postdata)
      if len(keywords.keys()) > 0:
        (results, statuscode) = search_api.searchGitlabSnippets(keywords.keys())
        if statuscode != 200:
          error_safety += 1
          ec.setSafetyCount('gitlab_snippet', error_safety)
          postdata = '_gitlab_snippet_ failed to search.\nStatus Code: ' + str(statuscode)
          master.postAnyData(postdata, channel)
          logger.info(postdata)
          if error_safety > safe_limit:
            postdata = 'Too Many Errors. _Gitlab Snippet_ Module is disabled for safety'
            ec.disable('gitlab_snippet')
            master.postAnyData(postdata, channel)
            logger.info(postdata)
        else:
          if error_safety != 0:
            ec.setSafetyCount('gitlab_snippet', 0)
          for word in keywords.keys():
            if word in results.keys():
              result = list(set(results[word]) - set(keywords[word][1]))
              if result != []:
                postdata = 'New Code Found about `' + word + '` in _gitlab_snippet_'
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                url = []
                for i in result:
                  url.append('https://gitlab.com' + i)
                  logger.info('https://gitlab.com' + i)
#                exclude = list(set(results[word]) & set(keywords[word][1]))
                exclude = results[word]
                master.postAnyData('\n'.join(url), channel)
                ec.clearExcludeList('gitlab_snippet', conf['Index'])
                ec.addExcludeList('gitlab_snippet', keywords[word][0], exclude)
  except:
    logger.error('--ERROR HAS OCCURED IN GITLAB SNIPPETS SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('gitlab_snippet', conf['Index'], False)

def runSearchPastebin():
  try:
    logger.info('--START PASTEBIN SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')
    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()
    keywords = {}
    channel = ''

    if 'keyword_pastebin' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_pastebin'].keys() and searchconf['keyword_pastebin']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 3
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_pastebin']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_pastebin']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_pastebin'].items():
        if conf['Index'] != 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              keywords[key] = (conf['Index'], conf['Exclude_list'])
            else:
              postdata = '`' + key + '` is expired in _pastebin_, and disabled.'
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('pastebin', conf['Index'], False)
              logger.info(postdata)
      if len(keywords.keys()) > 0:
        (results, statuscode) = search_api.searchPastebinRecent(keywords.keys())
        if statuscode != 200:
          error_safety += 1
          ec.setSafetyCount('pastebin', error_safety)
          postdata = 'pastebin serach failed in _pastebin_.\nStatus Code: ' + str(statuscode)
          master.postAnyData(postdata, channel)
          logger.info(postdata)
          if error_safety > safe_limit:
            postdata = 'Too Many Errors. _Pastebin_ Module is disabled for safety'
            ec.disable('pastebin')
            master.postAnyData(postdata, channel)
            logger.info(postdata)
        else:
          if error_safety != 0:
            ec.setSafetyCount('pastebin', 0)
          for word in keywords.keys():
            if word in results.keys():
              result = list(set(results[word]) - set(keywords[word][1]))
              if result != []:
                postdata = 'New Code Found about `' + word + '` in _pastebin_'
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                exclude = results[word]
                master.postAnyData('\n'.join(result), channel)
                ec.clearExcludeList('pastebin', conf['Index'])
                ec.addExcludeList('pastebin', keywords[word][0], exclude)
  except:
    logger.error('--ERROR HAS OCCURED IN PASTEBIN SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('pastebin', conf['Index'], False)

def runSearchGoogleCustom():
  try:
    engine_id = slackbot_settings.google_custom_search_engine_id
    api_key = slackbot_settings.google_custom_api_key
    logger.info('--START GOOGLE CUSTOM SEARCH--')
    now = datetime.date.today()
    today = now.strftime('%Y-%m-%d')

    conffile = open(configfile, 'r')
    searchconf = json.load(conffile)
    conffile.close()

    if 'keyword_google_custom' in searchconf.keys() and '__DEFAULT_SETTING__' in searchconf['keyword_google_custom'].keys() and searchconf['keyword_google_custom']['__DEFAULT_SETTING__']['Index'] == 0:
      safe_limit = 6
      error_safety = 0
      if '__SAFETY__' in searchconf['keyword_google_custom']['__DEFAULT_SETTING__'].keys():
        error_safety = searchconf['keyword_google_custom']['__DEFAULT_SETTING__']['__SAFETY__']
      for key, conf in searchconf['keyword_google_custom'].items():
        if conf['Index'] != 0:
          limittime = datetime.datetime.strptime(conf['Expire_date'], '%Y-%m-%d').date()
          if conf['Enable'] == True:
            channel = conf['Channel']
            if now < limittime:
              (result, statuscode) = search_api.googleCustomSearch(key, engine_id, api_key)
              result_post = list(set(result.keys()) - set(conf['Exclude_list']))
              if statuscode != 200:
                error_safety += 1
                ec.setSafetyCount('google_custom', error_safety)
                postdata = '`' + key + '` failed to search in _google_custom_.\nStatus Code: ' + str(statuscode)
                master.postAnyData(postdata, channel)
                logger.info(postdata)
                if error_safety > safe_limit:
                  postdata = 'Too Many Errors. _Google Custom_ Module is disabled for safety'
                  ec.disable('google_custom')
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
              else:
                if error_safety != 0:
                  ec.setSafetyCount('google_custom', 0)
                if result_post != []:
                  postdata = 'New Code Found about `' + key + '` in _google_custom_'
                  master.postAnyData(postdata, channel)
                  logger.info(postdata)
                  for i in result_post:
                    logger.info(i)
                    post_code = result[i][0] + '\n' + i + '\n'
                    master.postAnyData(post_code, channel)
#                  exclude = list(set(result.keys()) & set(conf['Exclude_list']))
                  exclude = result.keys()
                  ec.clearExcludeList('google_custom', conf['Index'])
                  ec.addExcludeList('google_custom', conf['Index'], exclude)
              time.sleep(30)
            else:
              postdata = '`' + key + '` is expired in _google_custom_, and disabled.'
              master.postAnyData(postdata, channel)
              ec.enableKeywordSetting('google_custom', conf['Index'], False)
              logger.info(postdata)
  except:
    logger.error('--ERROR HAS OCCURED IN GOOGLE CUSTOM SEARCH--')
    logger.error(traceback.format_exc())
    master.postAnyData(traceback.format_exc(), slackbot_settings.channels[0])
#    ec.enableKeywordSetting('google_custom', conf['Index'], False)

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
  jobConfigs = []

  try:
    slackbot_settings.API_TOKEN
  except NameError:
    sys.exit()
    print('Slackbot API TOKEN is required')

  start_state = []

  try:
    channels = slackbot_settings.channels
    if type(channels) != list or channels == []:
      print('Set more than 1 channel')
      sys.exit()
    channelfile = os.path.normpath(os.path.join(base, './settings/channellist'))
    cl = open(channelfile, 'w')
    cl.write('\n'.join(channels))
    cl.close()

    if slackbot_settings.enable_github_search:
      default_github = slackbot_settings.github_default_settings
      ret = ec.setDefaultSettings('github', default_github, channels)
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
      ret = ec.setDefaultSettings('github_code', default_github_code, channels)
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
      ret = ec.setDefaultSettings('gist', default_gist, channels)
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
      ret = ec.setDefaultSettings('gitlab', default_gitlab, channels)
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
      ret = ec.setDefaultSettings('gitlab_snippet', default_gitlab_snippet, channels)
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
      ret = ec.setDefaultSettings('pastebin', default_pastebin, channels)
      if ret:
        pastebin_snippet_interval = slackbot_settings.pastebin_search_interval
        jobConfigs.append(JobConfig(CronTab(pastebin_snippet_interval), runSearchPastebin))
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
      ret = ec.setDefaultSettings('google_custom', default_google_custom, channels)
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
  except NameError:
    print('slackbot_settings is something wrong')
    sys.exit(0)

  postdata = '---CodeScraper Slackbot Started---\n```'
  for m in start_state:
    postdata += ' : '.join(m) + '\n'
  postdata += '```'
  master.postAnyData(postdata, channels[0])
  print(postdata)

  p = Pool(len(jobConfigs) + 1)
  try:
    p.apply_async(runBot)
    p.map(job_controller, jobConfigs)
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  main()
