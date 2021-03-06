FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
COPY requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /src
WORKDIR /src
