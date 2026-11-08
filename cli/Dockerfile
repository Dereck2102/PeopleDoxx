FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx click

COPY peopledoxx_cli.py .

ENTRYPOINT ["python", "peopledoxx_cli.py"]
CMD ["--help"]

