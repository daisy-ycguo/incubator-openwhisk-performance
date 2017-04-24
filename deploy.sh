#!/bin/sh

# common docker setup
sudo gpasswd -a travis docker
sudo -E bash -c 'echo '\''DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock --storage-driver=overlay --userns-remap=default"'\'' > /etc/default/docker'
sudo service docker restart

# checkout openwhisk latest
git clone --depth 1 https://github.com/openwhisk/openwhisk.git

# install ansible
pip install --user ansible==2.1.2.0

cd openwhisk/ansible
ANSIBLE_CMD="ansible-playbook -i environments/local -e docker_image_prefix=openwhisk"

$ANSIBLE_CMD setup.yml
$ANSIBLE_CMD prereq.yml
$ANSIBLE_CMD couchdb.yml
$ANSIBLE_CMD initdb.yml
$ANSIBLE_CMD apigateway.yml
$ANSIBLE_CMD wipe.yml
$ANSIBLE_CMD openwhisk.yml