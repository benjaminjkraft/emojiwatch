PROJECT="emojiwatch"

serve:
	dev_appserver.py --port 8090 --admin_port 8010 app.yaml

deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with\n\tslack_bot_token = 'xoxb-...'\nin it." ; exit 1 )
	gcloud preview app deploy app.yaml cron.yaml --promote --project $(PROJECT)

.PHONY: serve deploy
