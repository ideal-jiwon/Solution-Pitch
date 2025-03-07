#!/bin/bash

# 패키지 설치
pip install -r requirements.txt

# Gunicorn 실행 (Flask 서버)
exec gunicorn -w 4 -b 0.0.0.0:8000 server:app

