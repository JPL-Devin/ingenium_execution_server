.PHONY: helping hand

IMAGE=lmestar/ingenium-exec-server
CONTAINER_NAME=exec_server

all: build run

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm --link exec_gateway:exec_gateway --name=exec_server -d -p 9999:9999 $(IMAGE)
	#docker run --rm -it --entrypoint=bash --expose 8888 --link exec_gateway:exec_gateway --name=exec_server -p 9999:9999 $(IMAGE)

stop:
	docker stop $(CONTAINER_NAME)
