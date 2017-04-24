#!/bin/sh
set -e

host=$1
credentials=$2
concurrency=$3

action="noop"

# create a noop action
echo "Creating noop action"
curl -u "$credentials" "$host/api/v1/namespaces/_/actions/$action" -XPUT -d '{"namespace":"_","name":"test","exec":{"kind":"nodejs:default","code":"function main(){return {};}"}}' -H "Content-Type: application/json"

# run the noop action
echo "Running noop action once to assert an intact system"
curl -u "$credentials" "$host/api/v1/namespaces/_/actions/$action?blocking=true" -XPOST

# run latency tests
docker run --rm markusthoemmes/loadtest loadtest -n 10000 -k -m POST -H "Authorization: basic $(echo $credentials | base64 -w 0)" "$host/api/v1/namespaces/_/actions/$action?blocking=true"

# run maximum throughput tests
docker run --rm markusthoemmes/loadtest loadtest -n 10000 -c "$concurrency" -k -m POST -H "Authorization: basic $(echo $credentials | base64 -w 0)" "$host/api/v1/namespaces/_/actions/$action?blocking=true"