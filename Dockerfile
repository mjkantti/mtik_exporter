FROM python:3-alpine

ENV VIRTUAL_ENV=/home/exporter/venv
ENV PROMETHEUS_DISABLE_CREATED_SERIES=True

WORKDIR /mtik_exporter
COPY . .

RUN addgroup -S exporter && adduser -S exporter -G exporter
USER exporter

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
RUN python -c 'from mac_vendor_lookup import MacLookup; MacLookup().update_vendors()'

EXPOSE 49090
CMD ["python", "/mtik_exporter/export.py"]
