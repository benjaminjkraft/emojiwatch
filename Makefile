PROJECT="emojiwatch2"

serve:
	dev_appserver.py --port 8090 --admin_port 8010 app.yaml

deploy:
	@[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with\n\tVERIFICATION_TOKEN = '...'\n(and perhaps CLIENT_ID and CLIENT_SECRET) in it." ; exit 1 )
	gcloud app deploy app.yaml --project $(PROJECT)

.PHONY: serve deploy
