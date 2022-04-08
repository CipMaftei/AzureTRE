FROM python:3.8-slim-buster
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /e2e
WORKDIR /e2e

CMD ["sh", "-c", "./run_tests_and_exit_succesfully.sh"]
