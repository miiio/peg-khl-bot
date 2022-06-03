FROM python:3.6.8

RUN mkdir /app
# &&apt-get update \
# &&apt-get -y install freetds-dev \
# &&apt-get -y install unixodbc-dev
WORKDIR /app
COPY bot.py bot.py
COPY aram.py aram.py
COPY hero_list.json hero_list.json
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD [ "python", "bot.py"]