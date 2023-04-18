#!/bin/bash

chmod 640 neo4j.conf

export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
export NEO4J_DOCKER_IMAGE=bitnami/neo4j:5
export NEO4J_EDITION=docker_compose
export EXTENDED_CONF=yes
export NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
export NEO4J_AUTH=neo4j/your_password

docker compose up -d
