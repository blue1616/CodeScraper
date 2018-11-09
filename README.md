# CodeScraper

## Description
CodeScraper is Slackbot that searches sites such as Github, Gitlab, Pastebin with pre-registered keywords and notifies you when it finds new ones.

Currently the following functions are implemented.

|Function|Description|Notes|
|---|---|---|
|github|Search Github and find new repositories||
|gist|Search Github and find new Gist||
|github_code|Do Github code search<br>it depends on Github Index|Github API Token is required|
|gitlab|Search Gitlab and find new projects||
|gitlab_snippet|Scraping new posts of Gitlab Snippets|Use Regular Expression.<br>Sometimes, it doesn't work well|
|google_custom|Search with Google Custom Search and find web pages|Make Search Engine and set your Engine ID and API Token.<br>Free Google API has limit of 100 requests per day|
|pastebin|Scraping Pastebin with Scraping API|Pastebin PRO Account(Paid Account) is required.<br>Use Regular Expression|

## Requirements
It is supposed to run using Docker

Otherwise you need Python 3 and the following libraries
 - slackbot (https://github.com/lins05/slackbot)
 - lxml
 - crontab

## Install
Using Docker

```sh
docker build -t codescraper .
```

Without using Docker

```sh
pip3 install -r requirements
```

## Usage
### Run CodeScrapter
You need slackbot_settings.py.
Create your setting file.

```sh
mv ./master/slackbot_settings.py.sample ./master/slackbot_settings.py
vim ./master/slackbot_settings.py
```

Edit your config file
- Required settings
  - API_TOKEN (Line 6)
    - Log in Slack and access [here](https://my.slack.com/services/new/bot). Create your Slackbot.
    - Set your Slackbot API Token
  - channels(Line 17-19)
    - Set slack channels that your slackbot join
    - At least one channel must be listed
  - Enable Targets(Line 87-94)
    - Select whether to enable each search target(True|False)
    - Separate settings are required to activate the following targets
      - github_code : github_access_token must be set
      - pastebin : Pastebin PRO account(Paid Account) and Static IP is required. You have to set your static IP to whitelist for using scraping API
      - google_custom : google_custom_api_key and google_custom_search_engine_id must be set
  - default_settings(Line 23-74)
    - Default settings of earh target
    - At least, change 'Channel' to one that slackbot join
    - The contents of each item are as shown in the table below

|item|Description|
|---|---|
|Enable|Set whether a keyword is enable or not(True&#124;False)|
|SearchLevel|Set search range in github or github_code(1&#124;2). Search level 2 searchs for wider range than 1|
|Time_Range|Set Search Time Range in github or gist. Items created before the set number of days are searched|
|Expire_date|Set keyword expiration date. The expiration date will be after the number of days set here, from the date at the time of registration. The keywords that have expired will be invalidated|
|Exclude_list|Notice exclusion list. This setting is unnecessary as scripts automatically rewrites.|
|Channel|Set up the channel to be notified|

- Optional settings
  - github_access_token(Line 78)
    - It requires if github_code is enabled
    - Get from [here](https://github.com/settings/tokens)
  - google_custom_api_key(Line 83)
    - It requires if google_custom is enabled
    - Get from [here](https://console.developers.google.com/)
  - google_custom_search_engine_id
    - It requires if google_custom is enabled
    - Get from [here](https://console.developers.google.com/)
  - Interval(Line 97-106)
    - Set search execution time for each search target
    - Set in crontab format

Run docker container with sharing your setting file.

```sh
docker run -d --name codescraper -v $PWD/master/slackbot_settings.py:/home/codescraper/master/slackbot_settings.py codescraper
```

After successful launch, Slcak will receive the following notification
> ---CodeScraper Slackbot Started---
>
> github : SUCCESS : Started <br>
> gist : SUCCESS : Started <br>
> gitlab : SUCCESS : Started <br>

### CodeScraper Commands
Search keywords are operated by commands via Slackbot

First, following command displays help

```
@{Slackbot name} help:
```

```
Command Format is Following:
    {Command}: {target}; {arg1}; {arg2}; ...

Command List:

'setKeyword: target; [word]'    Add [word] as New Search Keyword with Default Settings.
(abbreviation=setK:)
'enableKeyword: target; [index]'    Enable the Search Keyword indicated by [index].
(abbreviation=enableK:)
'disableKeyword: target; [index]'    Disable the Search Keyword indicated by [index].
(abbreviation=disableK:)
'setSearchLevel: target; [index]'    Set Search Level of Github Search (1:easily 2:) indicated by [index]. It is used in github and github_code.
(abbreviation=setSL:)
'setExpireDate: target; [index]; [expiration date]'    Set a Expiration Date of the Keyword indicated by [index]. [expiration date] Format is YYYY-mm-dd.
(abbreviation=setED:)
'setChannel: target; [index];[channel]'    Set channel to notify the Search Keyword's result.
(abbreviation=setC:)
'getKeyword: target;'    Listing Enabled Search Keywords.
(abbreviation=getK:)
'getAllKeyword: target;'    Listing All Search Keyword (include Disabled Keywords).
(abbreviation=getAllK:)
'getSearchSetting: target; [index]'    Show Setting of the Search Keyword indicated by [index].
(abbreviation=getSS:)
'help:'    Show this Message.

Target:
    github
    gist
    github_code
    gitlab
    gitlab_snippet (Use RE match)
    google_custom
    pastebin (Use RE match)
```

Register Keywords to send commands to Slackbot.

Commands are below.
See 'help:' command for specific usage.

|Command|Description|Search targets|
|---|---|---|
|setKeyword:|Register new search keyword|all|
|enableKeyword:|Enable specified search keyword|all|
|disableKeyword:|Disable specified search keyword|all|
|setSearchLevel:|Set Search Range of specified search keyword|github, github_code|
|setExpireDate:|Set expiration date of specified search keyword|all|
|setChannel:|Set channel to notify of specified search keyword|all|
|getKeyword:|Display lists of Enabled Keywords|all|
|getAllKeyword:|Display lists of all registered keyword|all|
|getSearchSetting:|Display current settings of specified search keyword|all|
|help:|Display help|-|

The index is assigned to each search keywords. To change the setting, specify the index.
The index of each keyword can be known by keyword registration or by 'getKeyword:' command.

![CodeScraper-1](img/codescraper-1.png)

Notification on finding Github new repository

![CodeScraper-2](img/codescraper-2.png)

### Notices
- Pastebin
  - Pastebin PRO Account（Paid Account） is required.
  - Access [here](https://pastebin.com/doc_scraping_api) and set your static IP you run CodeScraper to whitelist
  - Static IP is required.
- Google Custom Search
  - Free Google API has limit of 100 requests per day
  - If you set search interval to every 2 hour, you can register at most 8 search keywords (12 * 8 = 96 reqs). Be aware that there is a limit on the number of keywords depending on the frequency of search

## Author
[blueblue](https://twitter.com/piedpiper1616)
