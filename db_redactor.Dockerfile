FROM python:3.8.10

RUN mkdir -p /usr/src/app/

COPY src/db_redactor/ /usr/app/
WORKDIR /usr/app/

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "db_redactor_main.py"]
