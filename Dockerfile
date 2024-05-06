FROM python:3-alpine

ENV VIRTUAL_ENV=/home/mktxp/venv

WORKDIR /mtik_exporter
COPY . .

RUN chmod +x export.py

RUN addgroup -S mktxp && adduser -S mktxp -G mktxp
USER mktxp

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
EXPOSE 49090
CMD ["python", "/mtik_exporter/export.py"]
