FROM python:3.10.6

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PATH "$PATH:/app/scripts"

RUN useradd -m -d /app -s /bin/bash app \
    && chown -R app:app /app/* && chmod a+x /app/scripts/*

WORKDIR .

CMD [ "./scripts/start_test.sh" ]

