FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./gis_project /code
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache gcc zlib-dev jpeg-dev musl-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

VOLUME ["/code"]

