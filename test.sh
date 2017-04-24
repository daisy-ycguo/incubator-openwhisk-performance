#!/bin/sh

# create a noop action
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/curlTest" -XPUT -d '{"namespace":"_","name":"test","exec":{"kind":"nodejs:default","code":"function main(){return {};}"}}' -H "Content-Type: application/json"

# run the noop action
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/curlTest?blocking=true" -XPOST