#!/bin/sh
set -e
currentDir="$(dirname "$0")"

# Host to use. Needs to include the protocol.
host=$1
# Credentials to use for the test. USER:PASS format.
credentials=$2
# concurrency level of the throughput test: How many requests should
# open in parallel.
concurrency=$3
# How many samples to create by the test. Default: 10000
samples=${4:-10000}

action="noopThroughput"
"$currentDir/create.sh" "$host" "$credentials" "$action"

# run throughput tests
encodedAuth=$(echo "$credentials" | base64 -w 0)
docker run --rm markusthoemmes/loadtest loadtest -n "$samples" -c "$concurrency" -k -m POST -H "Authorization: basic $encodedAuth" "$host/api/v1/namespaces/_/actions/$action?blocking=true"