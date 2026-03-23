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