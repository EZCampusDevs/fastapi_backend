FROM python:3-alpine

ARG DIR="/opt/fastapi"

RUN mkdir $DIR

# does ./ copy from local dir?
COPY . $DIR

#COPY .env $DIR

RUN pip install -r $DIR/requirements.txt

RUN chmod +x $DIR/entrypoint.sh

ENTRYPOINT ["/opt/fastapi/entrypoint.sh"]
