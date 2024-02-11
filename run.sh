# this file must not be run from parent or another directory!
# just cd into this file directory and then: sh run.sh or ./run.sh

python3.12 -m venv venv

./venv/bin/pip install -r requirements.txt
./venv/bin/pip install -e . --upgrade

./venv/bin/python3.12 FreeV2ray/app.py
