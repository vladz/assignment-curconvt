FROM python:slim
LABEL maintainer='vlad.zverev@gmail.com'

COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD /curconvt /curconvt

WORKDIR /

CMD ["python", "-m", "curconvt"]
