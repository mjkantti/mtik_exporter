FROM python:3-alpine

ENV VIRTUAL_ENV=/home/exporter/venv
ENV MAC_VENDORS_CACHE=$VIRTUAL_ENV/cache/mac-vendors.txt
ENV PROMETHEUS_DISABLE_CREATED_SERIES=True

WORKDIR /mtik_exporter
COPY . .

RUN addgroup -S exporter && adduser -S exporter -G exporter
USER exporter

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
# Download the MAC vendor list through the same code the exporter uses, so it ends up in the path used at runtime
RUN mkdir -p $(dirname $MAC_VENDORS_CACHE) && python -c "from utils.utils import mac_lookup; mac_lookup.update_vendors()"

EXPOSE 49090
CMD ["python", "/mtik_exporter/export.py"]
