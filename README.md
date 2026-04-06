# PyRansom — Educational Ransomware Simulation

A Python-based ransomware simulation and C2 (command and control) server built 
for educational use at Champlain College's Leahy Center for Digital Forensics & 
Cybersecurity. This project is a port of an earlier C# implementation, rewritten 
in Python to make the internals more readable for students learning about malware 
behavior and incident response.

## Purpose

This project exists to help students understand:
- How ransomware communicates with a C2 server
- How encryption keys are managed in a ransomware attack
- What network indicators of compromise (IOCs) look like
- How to build detection and response strategies against this class of threat

## ⚠️ Legal Notice & Intended Use

This software is provided **strictly for authorized educational and research 
purposes** within controlled lab environments.

- **Do not deploy this on any system you do not own and have explicit written 
  permission to test.**
- **Do not use this against real targets, production systems, or any system 
  outside of an isolated lab environment.**
- Unauthorized deployment of ransomware is a federal crime under the Computer 
  Fraud and Abuse Act (CFAA) and equivalent laws in other jurisdictions. 
  Violations can result in significant prison time and fines.
- The author and Champlain College assume **no liability** for misuse of this 
  software.

By cloning or using this repository you agree that you are doing so solely for 
lawful educational purposes.

## Environment

All testing should be performed in an **isolated, air-gapped virtual machine** 
with no access to production networks or real user data. Recommended setup:
- VMware or VirtualBox with host-only networking
- Snapshots taken before each test run
- No shared folders or clipboard with the host OS

## Project Structure
```
/c2         C2 server — manages connections, issues commands
/payload    Simulated ransomware client
```
## Target
### Config File
In the target directory you can see a file called config.py. This file contains constants that are required for the program to work.

| Config      | Purpose                                                                         | Defaut    |
| ----------- | ------------------------------------------------------------------------------- | --------- |
| RETRY_TIME  | The number of seconds the script will wait before trying to reccocent to sever. | 5         |
| HOST        | The IP of the c2 server                                                         | 127.0.0.1 |
| PORT        | The port of the c2 server                                                       | 8080      |
| TARGET_DIR  | The first directory that will be recursed through for ransom                    | /home/    |
| BINARY_NAME | The output binary name                                                          | /example/ |
Ensure these configs are set how you want before building into a executable.

### Building
This program is intended for linux systems only! It has not been tested on windows.
In *Ransomware/payload* there is a build.sh. This script is built to automatically build the executable.
```bash
cd Ransomware/payload
chmod +x build.sh
./build.sh
```
After it is built you can access the executable at *Ransomware/payload/dist/*
This ELF is a standalone file and can be shared or moved to the intended directory.

### Running Payload
When you are ready to run the ransom you can use. 
```bash
sudo ./example
```

## Attacker

### Installation
Navigate to the c2 folder
```bash
cd RansomwareSim/c2
python3 -m venv venv # create venv
source venv/bin/activate # activate venv
pip3 install -r requirements.txt
```
Then to run the c2 server
```bash
python3 main.py
```

### Keymaps
`l` - List active connections
* In this menu select your target by pressing the corresponding number
`r` - Ransomware option
* When a target/targets is selected run ransomware on them
`t` - List active targets <br>
`q` - Quit <br>
`b` - Goes back in all menus <br>

### Ransomware Instructions
1. Wait for client to join
2. Once client is joined press `l` to list targets
3. Select your targets with the num keys `0-9`
4. Type `b` to go back
5. Type `r` to go to ransomware menu
6. Type `a` to attack every target
7. Wait for message saying it is encrypted
8. Wait for target to fill out form

## Acknowledgements

Built as part of coursework and lab development at the 
[Leahy Center for Digital Forensics & Cybersecurity](https://www.champlain.edu/leahy-center), 
Champlain College, Burlington VT.

