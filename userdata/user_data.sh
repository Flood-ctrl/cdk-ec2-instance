#!/bin/bash

mkdir /home/1234
for i in {0..3}; do
  touch /home/file-$i
done;
yum install git -y
yum install vim -y
yum install apache -y