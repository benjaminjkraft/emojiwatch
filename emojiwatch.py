# -*- coding: utf-8 -*-
import json
import urllib
import urllib2

from google.appengine.ext import ndb
import webapp2

import secrets

# The channel we post to
CHANNEL_NAME = '#emojiwatch'
_SLACK_API_URL = 'https://slack.com/api/'


class EmojiList(ndb.Model):
    """Singleton to store the current list of emoji."""
    emoji = ndb.JsonProperty()


def hit_slack_api(method, data=None):
    if data is None:
        data = {}
    data['token'] = secrets.slack_bot_token
    data['as_user'] = True
    res = urllib2.urlopen(_SLACK_API_URL + method,
                          data=urllib.urlencode(data))
    decoded = json.loads(res.read())
    if not decoded['ok']:
        raise RuntimeError("not ok, slack said %s" % decoded)
    return decoded


def get_new_emoji():
    return hit_slack_api('emoji.list')['emoji']


def get_old_emoji():
    emoji_list = EmojiList.get_by_id('()')
    if not emoji_list:
        return {}
    else:
        return emoji_list.emoji


def save_emoji(emoji):
    return EmojiList(id='()', emoji=emoji).put()


def format_single_attachment(verb, name, value):
    if value.startswith('http'):
        return {
            "mrkdwn_in": ["text"],
            "text": "*%s*: `:%s:`" % (verb, name),
            "image_url": value,
        }
    else:
        return {
            "mrkdwn_in": ["text"],
            "text": "*%s*: `:%s:` (%s)" % (verb, name, value),
        }


def format_diff(old, new):
    attachments = []
    for name, value in new.iteritems():
        if value != old.get(name):
            attachments.append(
                format_single_attachment("Added", name, value))
    for name, value in old.iteritems():
        if value != new.get(name):
            attachments.append(
                format_single_attachment("Removed", name, value))
    return attachments


def send_message(channel, attachments):
    hit_slack_api('chat.postMessage', {
        'channel': channel,
        'attachments': json.dumps(attachments),
        'unfurl_media': True})


class Watch(webapp2.RequestHandler):
    def get(self):
        """Invoked by cron."""
        old = get_old_emoji()
        new = get_new_emoji()
        diff = format_diff(old, new)
        if diff:
            send_message(CHANNEL_NAME, diff)
        save_emoji(new)


app = webapp2.WSGIApplication([
    ('/watch', Watch),
])
