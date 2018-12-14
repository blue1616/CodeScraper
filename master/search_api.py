import requests
import lxml.html
import datetime
import time
import json
import os.path
import urllib
import re
import feedparser
from dateutil import parser, tz
#import traceback
from pyquery import PyQuery

'''def get_request(url, headers, tries, timeout):
  try:
    if tries < 0:
      r = requests.get(url, headers=headers timeout=timeout)
      return r
    else:
      return None
  except requests.exceptions.ConnectTimeout:
    sleep(1.5)
    res = requestX(url, headers, tries-1, timeout)
    return res'''

def searchGithub(word, day, level):
  searchlevel = {
    1: 'in:name,descrition',
    2: 'in:name,descrition,readme',
    3: 'in:name,descrition,readme'}
  github_url = 'https://api.github.com/search/repositories?q='
  try:
    if word.find(' ') > 0:
      word.replace(' ', '\" \"')
    word = urllib.parse.quote('\"' + word + '\"')
    url = github_url + word + '+' + searchlevel[level] + '+created:>' + day
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}
    result = requests.get(url, timeout=10, headers=headers)
    statuscode = result.status_code
    resultdata = result.json()
    codes = []
    for a in resultdata['items']:
      name = a['full_name']
      if a['size'] > 0:
        codes.append(name)
    return codes, statuscode
  except:
    return [], -1

def searchGithubCode(word, level, api_key):
  searchlevel = {
    1: 'in:file',
    2: 'in:file,path',
    3: 'in:file,path'}
  github_url = 'https://api.github.com/search/code?q='
  try:
    if word.find(' ') > 0:
      word.replace(' ', '\" \"')
    word = urllib.parse.quote('\"' + word + '\"')
    url = github_url + word + '+' + searchlevel[level] + '+sort%3Aindexed&access_token=' + api_key
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}
    result = requests.get(url, timeout=10, headers=headers)
    statuscode = result.status_code
    resultdata = result.json()
    codes = []
    for a in resultdata['items']:
      name = a['html_url']
      if level == 3:
        if not a['name'].lower().startswith('readme'):
          codes.append(name)
      else:
        codes.append(name)
    return codes, statuscode
  except:
    return [], -1

def searchGist(word, day):
  if word.find(' ') > 0:
    word.replace(' ', '\" \"')
  word = urllib.parse.quote('\"' + word + '\"')
  url = 'https://gist.github.com/search?utf8=%E2%9C%93&q=' + word + '+created%3A>' + day + '&ref=searchresults'
  try:
    result = requests.get(url, timeout=10)
    statuscode = result.status_code
    root = lxml.html.fromstring(result.text)
    codes = []
    for a in root.xpath('//div/a[@class="link-overlay"]'):
#      name = a.text_content()
      link = a.get('href')
      codes.append(link)
    return codes, statuscode
  except:
    return [], -1

def searchGitlab(word):
  try:
    if word.find(' ') > 0:
      word.replace(' ', '\" \"')
    word = urllib.parse.quote('\"' + word + '\"')
    url = 'https://gitlab.com/explore/projects?utf8=%E2%9C%93&name=' + word + '&sort=latest_activity_desc'
    result = requests.get(url, timeout=10)
    statuscode = result.status_code
    root = lxml.html.fromstring(result.text)
    codes = []
    for a in root.xpath('//div/a[@class="project"]'):
  #    name = a.text_content()
      link = a.get('href')
      codes.append(link)
    return codes, statuscode
  except:
    return [], -1

def searchGitlabSnippets(words):
  try:
    url = 'https://gitlab.com/explore/snippets'
    result = requests.get(url, timeout=10)
    statuscode = result.status_code
    snippets = []
    root = lxml.html.fromstring(result.text)
    symbols = r'[!\"#$%&\'()*+,\-./:;<=>@\[\]^_{|}~\\]'
    re_symbol = re.compile(symbols)
    pattlist = {}
    wordlist = {}
    for w in words:
      if re.search(re_symbol, w):
        pattlist[w] = re.compile(w)
      else:
        wordlist[w] = w.split(' ')
    for a in root.xpath('//div[@class="title"]/a'):
      name = a.text_content()
      link = a.get('href')
      snippets.append([name, link])
    codes = {}
    if statuscode == 200:
      for l in snippets:
        raw_url = 'https://gitlab.com' + l[1] + '/raw'
        raw_result = requests.get(raw_url, timeout=10)
        if raw_result.status_code == 200:
          for w, patt in pattlist.items():
            if re.search(patt, l[0]) or re.search(patt, raw_result.text):
              if w in codes.keys():
                codes[w].append(l[1])
              else:
                codes[w] = [l[1]]
          for w, patt in wordlist.items():
            matched = True
            for p in patt:
              if l[0].lower().find(p.lower()) < 0 and raw_result.text.lower().find(p.lower()) < 0:
                matched = False
            if matched:
              if w in codes.keys():
                codes[w].append(l[1])
              else:
                codes[w] = [l[1]]
        else:
          statuscode = raw_result.status_code
          break
        time.sleep(10)
    return codes, statuscode # dict, int
  except:
    return {}, -1

def getPasteList(limit):
  try:
    url = 'https://scrape.pastebin.com/api_scraping.php?limit=' + str(limit)
    result = requests.get(url, timeout=10)
    statuscode = result.status_code
    items = {}
    if statuscode == 200:
      scrape = result.json()
      for item in scrape:
        items[item["full_url"]] = [item["title"], item["scrape_url"]]
    return items, statuscode # dict, int
  except:
    return {}, -1

def scrapePastebin(words, items):
  codes = {}
  statuscode = -1
  symbols = r'[!\"#$%&\'()*+,\-./:;<=>@\[\]^_{|}~\\]'
  re_symbol = re.compile(symbols)
  try:
    pattlist = {}
    wordlist = {}
    for w in words:
      if re.search(re_symbol, w):
        if w.startswith('.*'):
          w = w[2:]
        if w.endswith('.*'):
          w = w[:-2]
        pattlist[w] = re.compile(w)
      else:
        wordlist[w] = w.split(' ')
    for k,v in items.items():
      raw_result = requests.get(v[1], timeout=10)
      statuscode = raw_result.status_code
      if statuscode == 200:
        for w, patt in pattlist.items():
          if re.search(patt, v[0]) or re.search(patt, raw_result.text):
            if w in codes.keys():
              codes[w].append(k)
            else:
              codes[w] = [k]
        for w, patt in wordlist.items():
          matched = True
          for p in patt:
            if v[0].lower().find(p.lower()) < 0 and raw_result.text.lower().find(p.lower()) < 0:
              matched = False
          if matched:
            if w in codes.keys():
              codes[w].append(k)
            else:
              codes[w] = [k]
      else:
        return {}, statuscode
      time.sleep(1.5)
    return codes, statuscode # dict, int
  except:
    return {}, -1

def googleCustomSearch(word, engine_id, api_key):
  try:
    if word.find(' ') > 0:
      word.replace(' ', '\" \"')
    word = urllib.parse.quote('\"' + word + '\"')
    headers = {"content-type": "application/json"}
    url = 'https://www.googleapis.com/customsearch/v1?key=' + api_key + '&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&cx=' + engine_id + '&q=' + word + '&sort=date'
    result = requests.get(url, timeout=10, headers=headers)
    statuscode = result.status_code
    codes = {}
    if statuscode == 200:
      jsondata = result.json()
      if 'items' in jsondata.keys():
        for item in jsondata['items']:
          name = item['title']
          sub = item['snippet']
          link = item['link']
          codes[link] = [name, sub]
    return codes, statuscode
  except:
    return {}, -1

def parseRSS(items):
  parseddata = []
  for item in items:
    data = {
      'link' : item['link']
    }
    if 'title' in item.keys():
      data['title'] = item['title']
    if 'summary' in item.keys():
      data['summary'] = item['summary']
    if 'updated' in item.keys() and item['updated'] != '':
      dt = parser.parse(item['updated'])
      if dt.tzinfo == None:
        data['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
      else:
        data['timestamp'] = dt.astimezone(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')
    elif 'published' in item.keys() and item['published'] != '':
      dt = parser.parse(item['published'])
      if dt.tzinfo == None:
        data['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
      else:
        data['timestamp'] = dt.astimezone(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')
    else:
      data['timestamp'] = None
    taglist = []
    if 'tags'in item.keys():
      for tag in item['tags']:
        taglist.append(tag['term'])
    data['tags'] = taglist
    contents = []
    if 'content'in item.keys():
      for c in item['content']:
        content = (c['type'], c['value'])
        contents.append(content)
    data['contents'] = contents
    parseddata.append(data)
  return parseddata

def getRSSFeeds(url, lastpost):
  try:
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    response = requests.get(url, timeout=10, headers=headers)
    updateditems = []
    statuscode = response.status_code
    if statuscode == 200:
      rss = feedparser.parse(response.text)
      result = parseRSS(rss['entries'])
      for entry in result:
  #      if entry['timestamp'] != None and lastpost['timestamp'] != None:
  #        if datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(lastpost['timestamp'], '%Y-%m-%d %H:%M:%S'):
  #          updateditems.append(entry)
  #      else:
        if entry['link'] != lastpost['link']:
          updateditems.append(entry)
        else:
          break
    return updateditems, statuscode
  except:
    return [], -1

def getTweets(users, word, lastpost):
  try:
    query = ''
    if word.strip() != '':
      query += word
    if len(users) == 1:
      query += ' from:' + users[0]
    elif len(users) > 1:
      query += ' from:' + ' OR from:'.join(users)
    query = urllib.parse.quote_plus(query)
    url = 'https://twitter.com/i/search/timeline?f=tweets&q={query}&src=typd'.format(query=query)
    headers = {
      'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',
      'Accept':"application/json, text/javascript, */*; q=0.01",
      'Accept-Language':"de,en-US;q=0.7,en;q=0.3",
      'X-Requested-With':"XMLHttpRequest",
      'Referer':url,
      'Connection':"keep-alive"
    }
    response = requests.get(url, headers=headers)
    statuscode = response.status_code
    tweetslist = []
    new_tweets = []
    res = response.json()
    if statuscode == 200:
      json_response = response.json()
      if json_response['items_html'].strip() != '':
        scraped_tweets = PyQuery(json_response['items_html'])
        scraped_tweets.remove('div.withheld-tweet')
        tweets = scraped_tweets('div.js-stream-tweet')
        if len(tweets) != 0:
          for tweet_html in tweets:
            t = {}
            tweetPQ = PyQuery(tweet_html)
            t['user'] = tweetPQ("span:first.username.u-dir b").text()
            txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text())
            txt = txt.replace('# ', '#')
            txt = txt.replace('@ ', '@')
            t['tweet'] = txt
            t['id'] = tweetPQ.attr("data-tweet-id")
            t['link'] = tweetPQ.attr("data-permalink-path")
            tweetslist.append(t)
      for tw in tweetslist:
        if tw['id'] == lastpost['id']:
          break
        new_tweets.append(tw)
    return new_tweets, statuscode
  except:
    return [], -1
