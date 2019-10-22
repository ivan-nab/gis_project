FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./gis_project /code
RUN pip install -r "requirements.txt"
VOLUME ["/project"]
WORKDIR /project
