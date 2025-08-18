FROM cae-artifactory.jpl.nasa.gov:17001/python:3.7.2

### Execution Server
WORKDIR /app
COPY ./image /app
RUN pip install -r requirements.txt

###
EXPOSE 9999
CMD ["python", "execution_server.py"]
