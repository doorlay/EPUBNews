#!/usr/bin/env bash
python3 -m venv . && source bin/activate
python3 -m pip install beautifulsoup4 -t src/
python3 -m pip install sendgrid -t src/
python3 -m pip install requests -t src/
python3 -m pip install -r requirements.txt