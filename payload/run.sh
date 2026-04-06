#!/bin/bash
if [[ $EUID -ne 0 ]]; then
	echo "This Script Needs to Be Run As Root"
	exit 1
fi

python3 main.py
