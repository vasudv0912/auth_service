FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/bookmybook

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt


# copy project
COPY . .
