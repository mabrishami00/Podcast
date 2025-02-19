FROM python:3.11.6-bullseye

WORKDIR /app

COPY . /app

ENV PYTHONUNBUFFERED=1

RUN python -m pip install --upgrade pip 
RUN pip install -r requirements.txt
                                  
EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]