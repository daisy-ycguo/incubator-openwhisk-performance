#!/bin/sh

action="noop"

# create a noop action
echo "Creating noop action"
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/$action" -XPUT -d '{"namespace":"_","name":"test","exec":{"kind":"nodejs:default","code":"function main(){return {};}"}}' -H "Content-Type: application/json"

# run the noop action
echo "Running noop action once to assert an intact system"
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/$action?blocking=true" -XPOST

# run performance harness
ab -n 1000 -m POST -k -A "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/$action?blocking=true"