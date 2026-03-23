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

## Acknowledgements

Built as part of coursework and lab development at the 
[Leahy Center for Digital Forensics & Cybersecurity](https://www.champlain.edu/leahy-center), 
Champlain College, Burlington VT.
