import server
import payment
import threading
import tui
import bus


# payment_thread = threading.Thread(
#     target=payment.app.run,
#     kwargs={
#         "host": "0.0.0.0",
#         "port": 5000,
#         "use_reloader": False,
#         "debug": False
#     }
# )
# payment_thread.daemon = True
# payment_thread.start()

b = bus.Bus()

t = tui.TUI(b)
tui_thread = threading.Thread(target=t.run)
tui_thread.start()

s = server.Server(b)
s.start()
s.run()

t.end()
quit()