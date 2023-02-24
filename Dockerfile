FROM python:3.11.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /src

COPY requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir -r /src/requirements.txt

COPY . /src/

CMD ["/src/docker-entrypoint.sh", "-n"]