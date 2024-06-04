FROM python:3.12.1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /

ENTRYPOINT ["python3", "/ted.py"]