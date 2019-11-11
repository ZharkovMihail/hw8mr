FROM python:3

RUN pip install redis && pip install flask && pip install pymongo

COPY server.py /

EXPOSE 5000

ENTRYPOINT ["python", "server.py"]
