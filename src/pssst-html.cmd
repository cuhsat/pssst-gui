@echo off
IF EXIST bower GOTO START

bower install

:START
python pssst-html.py %*
