FROM python:3.9

RUN pip install pipenv

WORKDIR /usr/src/app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0" ]