FROM python:3.12-slim

### Execution Server
WORKDIR /app
COPY ./image /app
RUN pip install -r requirements.txt

###
EXPOSE 9999
CMD ["python", "execution_server.py"]
