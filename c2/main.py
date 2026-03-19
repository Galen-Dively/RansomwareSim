import server
import payment
import threading

payment_thread = threading.Thread(
    target=payment.app.run,
    kwargs={
        "host": "0.0.0.0",
        "port": 5000,
        "use_reloader": False,
        "debug": False
    }
)
payment_thread.daemon = True
payment_thread.start()

s = server.Server()
s.start()
s.run()