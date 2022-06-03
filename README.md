```
docker build -tag khl-bot-docker .
docker run -d --restart unless-stopped -v /docker/khl/config:/app/config/ --name khl-bot khl-bot-docker
```