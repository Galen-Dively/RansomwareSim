#### CONFIGURATION ######
KEYSIZE = 2048 # Change to 4096 for harder encryption




payment_received = False

def toggle_payment():
    global payment_received
    payment_received = not payment_received
    print(f"[DEBUG] payment_received is now: {payment_received}")

def get_payment():
    return payment_received