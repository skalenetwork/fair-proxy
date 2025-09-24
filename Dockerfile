FROM python:3.11.13-slim-trixie

RUN apt-get update
RUN apt-get update && apt-get install -y swig gcc python3-dev libssl-dev

WORKDIR /usr/src/proxy

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/usr/src/proxy"
ENV COLUMNS=80

CMD ["python", "/usr/src/proxy/proxy/main.py"]
