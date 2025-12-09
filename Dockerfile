FROM python:latest

RUN mkdir -p /home/.teenychat

COPY . /home/.teenychat
WORKDIR /home/.teenychat

RUN python -m pip install -U pip
RUN python -m pip install -r requeriments.txt

EXPOSE 9892-9892

CMD ["flet", "run", "-w",  "main.py"]