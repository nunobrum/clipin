FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3-tk xclip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY clipin /app/clipin
COPY tests /app/tests
COPY run_unittests.py /app

CMD ["python3", "run_unittests.py"]