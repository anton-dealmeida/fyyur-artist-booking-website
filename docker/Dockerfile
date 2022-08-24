FROM python:3.10.5

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./startup.sh

ENV PORT=5000 \
    DEBUG=TRUE

ENTRYPOINT ["/usr/src/app/startup.sh" ]