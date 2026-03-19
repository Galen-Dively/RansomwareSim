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


# C2 Dev

1. Create Server waiting for multiple hosts. We need to use sockets for the connections.
```python
import socket
class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = socket.getaddrinfo(socket.gethostname())
        self.port = 4848
        self.running = False

    def start(self):
        self.sock.bind(('', self.port))
        self.sock.listen(5)
        self.running = True
        print("Succesfully Started C2 Server\nWaiting for connections...")

    def run(self):
        while self.running:
            conn, addr = self.sock.accept()
            print("Target Connected From ", addr)
            
	def handle_client(self, conn, addr):
		pass
```
This code is incomplete but currently it defines a Server Class, within that server class are four methods currently. We have the init function which creates a socket, gets address from hostname, sets port to 4848 and sets server state to running. The start function binds the address to the port creating a socket.  The run function starts the loop that waits for connections. There is a handle_client function. Currently we can only serve one client at a time, this could technically work for my demonstration but it is best to be able to handle multiple clients. To ensure we can do that we will use threading. We just need to add a couple of lines
2. Adding Threading
```python
import threading

	 def run(self):
        while self.running:
            conn, addr = self.sock.accept()
            print("Target Connected From ", addr)
            # Create new thread running handle_client
            t = threading.Thread(target=self.handle_client, args=(conn, addr,))
            t.start() # Start the thread
            
    def handle_client(self, conn: socket.socket, addr):
        while conn:
            try:
                data = conn.recv(2048)
                print("Recieved data", data.decode(), "from", addr)
                conn.send(data)
                print("Send Data:", data, addr)
            except Exception as e:
                print("Something went wrong", e)

```
We added to the handle_client function. While a connection is active try to get and send data, if something goes wrong catch it but still print it. The logic inside the handle_client will change as right now it s just a echo server. Using telnet we can see that it is working.


This Screenshot is from the target server. As we can see when we enter this a test the server sends it back to us.
![[Pasted image 20260319115941.png]]

This is the output from the c2 server
![[Pasted image 20260319120028.png]]

3. Simulate Fake Payment
Every Ransomware needs a payment system. Because this is a fake example we will create a fake page. It will just be a basic webpage with some sort of input. We will use flask for our site. To start install flask.
```bash
sudo apt install python3-pip
pip3 install Flask --break-system-packages
```
I should be using a virtual environment but sense there is only one script running on this box I will have it installed to system packages.

We need to create three new files. payment.py, payment.html, and globals.py. 
This is the code for payment.py
```python
from flask import Flask, request, render_template
import globals
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def pay():
    if request.method == "POST":
        yes = request.form.get("yes")
        no = request.form.get("no")
        if not no:
            return "Yikes..... Dont do that! Go back to payment page and answer correctly."
        if no:
            # Update payment recieved
            globals.toggle_payment()
            return "Payment Proccessed: Check your system!"
        return f"{yes, no}"
    return render_template("payment.html")
```
This creates  a function that checks the root of the directory. It accepts both gets and post methods. If it is a get method it returns are html if it is a post we process the payment. 

payment.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payments</title>
</head>
<body>
    <form action="{{ url_for('pay')}}" method="post">
        <label for="payment">Will you run random bash scripts as root? (Y/n)</label>
        <label for="yes">Yes: </label>
        <input type="checkbox" name="yes" id="yes">
        <label for="no">No: </label>
        <input type="checkbox" name="no" id="no">
        <button type="submit">Submit</button> 
    </form>
</body>
</html>
```
This is a basic html form asking if the user will run random bash scripts as root.

globals.py
```python
payment_recieved = False

def toggle_payment():
    if not payment_recieved:
        payment_recieved = True
    else:
        payment_recieved = False


def get_payment():
    return payment_recieved
```

I needed a place to store if the payment was made or not so the website and c2 server can interact. I am sure there is a better way to do this but I forget and dont want to figure it out.

4. C2 Server now needs to send data once payment recieved
