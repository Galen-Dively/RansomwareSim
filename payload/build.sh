#!/bin/bash

# Test Dependencies

response="$(python3 --version 2>&1)"
if [[ $? -eq 0 ]]; then
    echo "Found Python Installed"
else
    echo "Error: $response"
    exit 1
fi

response="$(pip3 --version 2>&1)"
if [[ $? -eq 0 ]]; then
    echo "Found Pip Installed"
else
    echo "Error: $response"
    exit 1
fi

# Create venv
echo "Creating Venv"
response="$(python3 -m venv venv 2>&1)"
if [[ $? -eq 0 ]]; then
    echo "venv created"
else
    echo "Error: $response"
    exit 1
fi

response="$(ls venv/bin/activate)"

if [[ $? -eq 0 ]]; then
    echo "Found activate script"
else
    echo "Error: $response"
    exit 1
fi

source venv/bin/activate 2>&1
# Install required packages

echo "Installing requirements"
response="$(pip3 install -r requirements.txt 2>&1)"
if [[ $? -eq 0 ]]; then
    echo "Requirements Installed"
else
    echo "Error: $response"
    exit 1
fi

# Try to compile
name="$(cat config.py | grep BINARY_NAME | cut -d ' ' -f 3 | tr -d '"')"
response="$(pyinstaller --onefile main.py --name $name 2>&1)"
if [[ $? -eq 0 ]]; then
    echo "Build Complete — executable is in dist/$name"
else
    echo "Error: $response"
    exit 1
fi