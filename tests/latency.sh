#!/bin/sh
set -e

# Host to use. Needs to include the protocol.
host=$1
# Credentials to use for the test. USER:PASS format.
credentials=$2
# How many samples to create by the test. Default: 10000
samples=${3:-10000} # default value of 10000

action="noopLatency"
./create.sh "$host" "$credentials" "$action"

# run latency tests
encodedAuth=$(echo "$credentials" | base64 -w 0)
docker run --rm markusthoemmes/loadtest loadtest -n "$samples" -k -m POST -H "Authorization: basic $encodedAuth" "$host/api/v1/namespaces/_/actions/$action?blocking=true"