FROM python:3

WORKDIR /opt/cfs/cfsCore
COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install autopep8
RUN python -m pip install -r requirements.txt