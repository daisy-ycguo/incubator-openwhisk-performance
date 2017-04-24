#!/bin/sh

action="noop"

# create a noop action
echo "Creating noop action"
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/$action" -XPUT -d '{"namespace":"_","name":"test","exec":{"kind":"nodejs:default","code":"function main(){return {};}"}}' -H "Content-Type: application/json"

# run the noop action
echo "Running noop action once to assert an intact system"
curl -u "$(cat openwhisk/ansible/files/auth.guest)" "172.17.0.1:10001/api/v1/namespaces/_/actions/$action?blocking=true" -XPOST

# run performance harness
docker run --rm markusthoemmes/loadtest loadtest -n 10000 -H "Authorization: basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" "http://172.17.0.1:10001/api/v1/namespaces/_/actions/$action?blocking=true" -m POST