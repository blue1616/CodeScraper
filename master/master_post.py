# -*- coding: utf-8 -*-

from slacker import Slacker
import slackbot_settings

def postNewPoCFound(word, repos, channel):
  url = 'https://github.com'
  slack = Slacker(slackbot_settings.API_TOKEN)
  slack.chat.post_message(
#    channel_vuln,
    channel,
    'New Code Found about `' + word  + '` at _github_',
    as_user=True
    )
  message = ''
  for r in repos:
    message += url + '/' + r + '/\n'
  slack.chat.post_message(
#    channel_vuln,
    channel,
    message,
    as_user=True
    )

def postAnyData(word, channel):
  slack = Slacker(slackbot_settings.API_TOKEN)
  slack.chat.post_message(
    channel,
    word,
    as_user=True
    )

#if __name__ == '__main__':
#  slack = Slacker(slackbot_settings.API_TOKEN)
#  slack.chat.post_message(
#    'bot_test',
#    'Hello. I\'m Master',
#    as_user=True
#    )
