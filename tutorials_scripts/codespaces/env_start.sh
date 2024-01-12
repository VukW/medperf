#!/usr/bin/env bash
echo "Preparing local medperf server..."
#source /medperf/venv/bin/activate
# we are located at /workspaces/medperf/ where repo is cloned to
pip install -e ./cli
pip install -r server/requirements.txt
pip install -r server/test-requirements.txt
medperf profile activate local

cd server
cp .env.local.local-auth .env
./setup-dev-server.sh &>server.log &
medperf auth login -e testmo@example.com
echo "Medperf is ready for local usage"
cd ..
#/bin/bash --rcfile medperfrc
