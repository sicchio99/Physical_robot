#!/bin/bash

# Configurazione
JETSON_NANO_USER="ubuntu"
JETSON_NANO_IP="192.168.0.110"
DOCKER_COMMANDS="docker start my_container || docker run -d --name my_container my_container"

ssh ${JETSON_NANO_USER}@${JETSON_NANO_IP} "${DOCKER_COMMANDS}"
