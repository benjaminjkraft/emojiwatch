emojiwatch
==========

A slack bot to notify you when someone adds a custom emoji.

![Screenshot of a new :potato: emoji](/screenshot.png?raw=true)

To install, head on over to [https://emojiwatch2.appspot.com/add](https://emojiwatch2.appspot.com/add).  (You may want to create an `#emojiwatch` channel first.)  If your emoji are super duper secret, see below to deploy your own instance.

Deploying
---------

`make deploy`.  You'll need to ask @benkraft for access.

To deploy your own instance:
* create a slack app, with a webhook
* set up secrets.py with your `VERIFICATION_TOKEN` from said slack app
* create a Google App Engine project
* change `PROJECT` in the `Makefile` to match your Google App Engine project
* manually set up the datastore entity for your team (TODO: how? or make it easier)
* `make deploy`
