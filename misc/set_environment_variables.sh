#!/bin/bash
read -s -p "Neo4j Username: " NEO4J_USER
echo -e "\n"
read -s -p "Neo4j Password: " NEO4J_PASS
export NEO4J_USER="${NEO4J_USER}"
export NEO4J_PASS="${NEO4J_PASS}"
