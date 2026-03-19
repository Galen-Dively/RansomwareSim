# RansomwareSim
A fake ransomware written in c# and python for learning purposes.

# Overview

RansomServer - This is the target server
C2 Server - This is where the private key is stored and processes payment

# Flow

1. C2 Server Active and listening 
2. Target Runs infected file
3. Target "pays ransom"
4. C2 Confirms then sends private key
5. Target Decrypts all files

