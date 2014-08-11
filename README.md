# tenderloin

A web-based multiplayer Mahjong client and server.


## Running it locally

```bash
pip install -r requirements.txt
python -m tenderloin.web
```


## Running it with docker

```bash
docker build -t="tenderloin" .
docker run -d -p 8000:8000 tenderloin
```

Then navigate to [http://dockerhost:8000]().
