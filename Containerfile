FROM python:3-alpine

ENV VIRTUAL_ENV=/home/exporter/venv

WORKDIR /mtik_exporter
COPY . .

RUN chmod +x export.py

RUN addgroup -S exporter && adduser -S exporter -G exporter
USER exporter

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
EXPOSE 49090
CMD ["python", "/mtik_exporter/export.py"]