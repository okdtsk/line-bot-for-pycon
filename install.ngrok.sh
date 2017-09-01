#!/bin/bash

cd $(dirname $0)

readonly NGROK_DOWNLOAD_PATH="https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"

mkdir -p bin
pushd bin > /dev/null
  wget -O ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip
  unzip ngrok.zip
  rm -f ngrok.zip
popd > /dev/null
