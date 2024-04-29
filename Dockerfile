FROM python:3-alpine
WORKDIR /mtik_exporter
COPY . .
RUN chmod +x export.py
RUN addgroup -S mtik_exporter && adduser -S mtik_exporter -G mtik_exporter
USER mtik_exporter
RUN pip install -r requirements.txt
EXPOSE 49090
ENTRYPOINT ["/mtik_exporter/export.py"]
