FROM python:3.11-bookworm

RUN apt-get update

WORKDIR /usr/src/proxy

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/usr/src/proxy"
ENV COLUMNS=80

CMD python /usr/src/proxy/proxy/main.py
