#!/bin/sh

images="controller invoker"
for i in $images
do
    docker pull "openwhisk/$i"
    docker tag "openwhisk/$i" $i
done