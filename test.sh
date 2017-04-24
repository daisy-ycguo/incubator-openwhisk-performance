#!/bin/sh
set -e

action="noop"
credentials="$(cat openwhisk/ansible/files/auth.guest)"
host="172.17.0.1:10001"

# create a noop action
echo "Creating noop action"
curl -u "$credentials" "$host/api/v1/namespaces/_/actions/$action" -XPUT -d '{"namespace":"_","name":"test","exec":{"kind":"nodejs:default","code":"function main(){return {};}"}}' -H "Content-Type: application/json"

# run the noop action
echo "Running noop action once to assert an intact system"
curl -u "$credentials" "$host/api/v1/namespaces/_/actions/$action?blocking=true" -XPOST

# run performance harness
docker run --rm markusthoemmes/loadtest loadtest -n 10000 -H "Authorization: basic $(echo $credentials | base64 -w 0)" "http://$host/api/v1/namespaces/_/actions/$action?blocking=true" -m POST