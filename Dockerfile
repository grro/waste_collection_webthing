FROM python:3-alpine

ENV port 8233
ENV directory /etc/waste_collection


RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/waste_collection_webthing.py $port $directory



