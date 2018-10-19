import requests
import lxml.html
import datetime
import time
import json
import os.path
import urllib
import re

def searchGithub(word, day, level):
  searchlevel = {
    1: 'in:name,descrition',
    2: 'in:name,descrition,readme',
    3: 'in:name,descrition,readme'}
  github_url = 'https://api.github.com/search/repositories?q='
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  url = github_url + word + '+' + searchlevel[level] + '+created:>' + day
  headers = {"Accept": "application/vnd.github.mercy-preview+json"}
  result = requests.get(url, headers=headers)
  statuscode = result.status_code
#  root = lxml.html.fromstring(result.text)
  resultdata = result.json()
  codes = []
#  for a in root.xpath('//h3/a'):
  for a in resultdata['items']:
    name = a['full_name']
    if a['size'] > 0:
      codes.append(name)
  return codes, statuscode

def searchGithubCode(word, level, api_key):
  searchlevel = {
    1: 'in:file',
    2: 'in:file,path',
    3: 'in:file,path'}
  github_url = 'https://api.github.com/search/code?q='
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  url = github_url + word + '+' + searchlevel[level] + '+sort%3Aindexed&access_token=' + api_key
  headers = {"Accept": "application/vnd.github.mercy-preview+json"}
  result = requests.get(url, headers=headers)
  statuscode = result.status_code
#  root = lxml.html.fromstring(result.text)
  resultdata = result.json()
  codes = []
#  for a in root.xpath('//h3/a'):
  for a in resultdata['items']:
    name = a['html_url']
    if level == 3:
      if not a['name'].lower().startswith('readme'):
        codes.append(name)
    else:
      codes.append(name)
  return codes, statuscode

def searchGist(word, day):
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  url = 'https://gist.github.com/search?utf8=%E2%9C%93&q=' + word + '+created%3A>' + day + '&ref=searchresults'
  result = requests.get(url)
  statuscode = result.status_code
  root = lxml.html.fromstring(result.text)
  codes = []
  for a in root.xpath('//div/a[@class="link-overlay"]'):
#    name = a.text_content()
    link = a.get('href')
    codes.append(link)
  return codes, statuscode

def searchGitlab(word):
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  url = 'https://gitlab.com/explore/projects?utf8=%E2%9C%93&name=' + word + '&sort=latest_activity_desc'
  result = requests.get(url)
  statuscode = result.status_code
  root = lxml.html.fromstring(result.text)
  codes = []
  for a in root.xpath('//div/a[@class="project"]'):
#    name = a.text_content()
    link = a.get('href')
    codes.append(link)
  return codes, statuscode

def searchGitlabSnippets(words):
  url = 'https://gitlab.com/explore/snippets'
  result = requests.get(url)
  statuscode = result.status_code
  snippets = []
  root = lxml.html.fromstring(result.text)
  for a in root.xpath('//div[@class="title"]/a'):
    name = a.text_content()
    link = a.get('href')
    snippets.append([name, link])
  codes = {}
  if statuscode == 200:
    for l in snippets:
      raw_url = 'https://gitlab.com' + l[1] + '/raw'
      raw_result = requests.get(raw_url)
      if raw_result.status_code == 200:
        for word in words:
          patt = re.compile(word, re.IGNORECASE)
          if re.search(patt, l[0]) or re.search(patt, raw_result.text):
  #        if l[0].find(word) > 0 or raw_resultw.text.find(word) > 0:
            print(l[1])
            if word in codes.keys():
              codes[word].append(l[1])
            else:
              codes[word] = [l[1]]
      else:
        statuscode = raw_result.status_code
        break
      time.sleep(10)
  return codes, statuscode # dict, int

def searchPastebinRecent(words):
  url = 'https://scrape.pastebin.com/api_scraping.php?limit=30'
  result = requests.get(url)
  statuscode = result.status_code
  items = {}
  codes = {}
  if statuscode == 200:
    try:
      scrape = result.json()
      for item in scrape:
        items[item["full_url"]] = [item["title"], item["scrape_url"]]
      for k,v in items.items():
        raw_result = requests.get(v[1])
        if raw_result.status_code == 200:
          for word in words:
            patt = re.compile(word, re.IGNORECASE)
            if re.search(patt, v[0]) or re.search(patt, raw_result.text):
              if word in codes.keys():
                codes[word].append(k)
              else:
                codes[word] = [k]
        else:
          statuscode = raw_result.status_code
          break
        time.sleep(1.5)
    except:
      return {}, -1
  return codes, statuscode # dict, int

def googleCustomSearch(word, engine_id, api_key):
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  headers = {"content-type": "application/json"}
  url = 'https://www.googleapis.com/customsearch/v1?key=' + api_key + '&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&cx=' + engine_id + '&q=' + word + '&sort=date'
  result = requests.get(url, headers=headers)
  statuscode = result.status_code
  codes = {}
  if statuscode == 200:
    jsondata = result.json()
#    print(jsondata.keys())
    if 'items' in jsondata.keys():
      for item in jsondata['items']:
        name = item['title']
        sub = item['snippet']
        link = item['link']
#        print([name, sub, url])
        codes[link] = [name, sub]
#    print(codes)
  return codes, statuscode
