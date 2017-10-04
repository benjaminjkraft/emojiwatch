# -*- coding: utf-8 -*-
import json
import logging
import urllib
import urllib2

from google.appengine.ext import ndb
import webapp2

import secrets

_SLACK_API_URL = 'https://slack.com/api/'


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


class SlackTeam(ndb.Model):
    """Stores the data we need for a particular team.

    Keyed by Slack team ID.
    """
    access_token = ndb.StringProperty()
    webhook = ndb.StringProperty()
    emoji = ndb.JsonProperty()

    def send_message(self, attachments):
        res = urllib2.urlopen(urllib2.Request(
            self.webhook,
            json.dumps({'attachments': attachments}),
            {'Content-Type': 'application/json'})).read()
        if res.lower().strip() != 'ok':
            raise RuntimeError("not ok, slack said %s" % res)

    def fetch_emoji(self):
        res = urllib2.urlopen(
            _SLACK_API_URL + 'emoji.list',
            # for some reason this doesn't support sending json
            urllib.urlencode({'token': self.access_token}))
        decoded = json.loads(res.read())
        if not decoded['ok']:
            raise RuntimeError("not ok, slack said %s" % decoded)
        return decoded

    def fill_emoji(self, bust_cache=False):
        if bust_cache or not self.emoji:
            self.emoji = self.fetch_emoji()['emoji']
            self.put()

    def handle_add(self, data):
        self.fill_emoji()
        self.emoji[data['name']] = data['value']
        self.send_message([
            format_single_attachment("Added", data['name'], data['value'])])
        self.put()

    def handle_remove(self, data):
        self.fill_emoji()
        self.send_message([
            format_single_attachment("Removed", name,
                                     self.emoji.pop(name, u'¯\_(ツ)_/¯'))
            for name in data['names']])
        self.put()


def handle_event(data):
    event = data['event']
    if event['type'] != 'emoji_changed':
        logging.error('unhandled event type %s', event['type'])
        return

    team = SlackTeam.get_by_id(data['team_id'])
    if not team:
        logging.error('invalid team %s', data['team_id'])
        return

    if event['subtype'] == 'add':
        team.handle_add(event)
    elif event['subtype'] == 'remove':
        team.handle_remove(event)
    else:
        logging.error('unhandled event subtype %s', event['subtype'])


class EventHook(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        logging.info(data)
        if data['token'] != secrets.VERIFICATION_TOKEN:
            logging.error('invalid token %s', data['token'])
            self.response.status = 403
            self.response.write('Invalid token')
        elif data['type'] == 'url_verification':
            self.response.write(data['challenge'])
        elif data['type'] == 'event_callback':
            handle_event(data)   # TODO(benkraft): defer this!
        else:
            logging.error('unhandled type %s', data['type'])


app = webapp2.WSGIApplication([
    ('/event_hook', EventHook),
])
