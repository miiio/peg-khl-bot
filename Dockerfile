FROM python:3.6.8

RUN mkdir /app \
&&apt-get update \
&&apt-get -y install freetds-dev \
&&apt-get -y install unixodbc-dev
WORKDIR /app
COPY bot.py bot.py
COPY dld.py dld.py
COPY hero_list.json hero_list.json
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

CMD [ "python", "bot.py"]