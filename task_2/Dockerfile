FROM python:3.12

ENV APP_HOME /task_2

WORKDIR $APP_HOME

COPY . .

RUN pip install pipenv
RUN pipenv install -r requirements.txt

ENTRYPOINT ["python", "test.py"]