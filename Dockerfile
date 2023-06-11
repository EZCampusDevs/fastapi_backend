FROM python:3-alpine

ARG DIR="/opt/fastapi"

RUN mkdir $DIR

# does ./ copy from local dir?
COPY fastapi_backend $DIR

COPY .env $DIR

RUN pip install -r $DIR/requirements.txt

ENTRYPOINT ["/opt/fastapi/run.sh"]