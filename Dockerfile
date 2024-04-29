FROM python:3-alpine

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /mtik_exporter
COPY . .

RUN chmod +x export.py

RUN pip install -r requirements.txt
EXPOSE 49090
CMD ["python", "/mtik_exporter/export.py"]
