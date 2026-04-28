#!/bin/bash
# Absolute path to virtual environment python interpreter
PYTHON=/home/capstone-pinball/venv/bin/python
# Absolute path to Python script
SCRIPT=/home/capstone-pinball/main.py
# Absolute path to output log file
LOG=/home/capstone-pinball/pinball.log
echo -e "\n####### STARTUP $(date) ######\n" >> $LOG
$PYTHON $SCRIPT >> $LOG 2>&1