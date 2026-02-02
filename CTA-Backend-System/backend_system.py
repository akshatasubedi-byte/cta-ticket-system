from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ---------- SYSTEM DATA ----------
USERS = {
    "myself": "ctasystem",
    "staff": "ticket2026"
}

ZONES = {
    1: "Central",
    2: "Midtown",
    3: "Downtown"
}

FARES = {
    "Adult": 2105,
    "Child": 1410,
    "Student": 1750,
    "Senior": 1025
}

# ---------- HELPERS ----------
def calculate_zones(start, end):
    return abs(end - start) + 1

def calculate_fare(zones, rate, qty):
    return zones * rate * qty

def save_log(voucher_text):
    with open("ticket_log.txt", "a") as file:
        file.write(voucher_text + "\n")

def generate_voucher(start, end, travellers, total_cost):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    zones = calculate_zones(start, end)

    voucher = {
        "date_time": now,
        "boarding_zone": ZONES[start],
        "destination_zone": ZONES[end],
        "zones_travelled": zones,
        "travellers": travellers,
        "total_travellers": sum(travellers.values()),
        "total_cost": round(total_cost / 100, 2)
    }

    # Save as text log
    text_voucher = (
        "\n----- CTA TRAVEL VOUCHER -----\n"
        f"Date & Time: {voucher['date_time']}\n"
        f"Boarding Zone: {voucher['boarding_zone']}\n"
        f"Destination Zone: {voucher['destination_zone']}\n"
        f"Zones Travelled: {voucher['zones_travelled']}\n"
    )
    for cat, qty in travellers.items():
        text_voucher += f"{cat}: {qty}\n"
    text_voucher += (
        f"Total Travellers: {voucher['total_travellers']}\n"
        f"Total Cost: {voucher['total_cost']} credits\n"
        "------------------------------\n"
    )

    save_log(text_voucher)
    return voucher

# ---------- ROUTES ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in USERS and USERS[username] == password:
        return jsonify({"success": True, "message": "Login successful."})
    else:
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route("/zones", methods=["GET"])
def get_zones():
    return jsonify(ZONES)

@app.route("/fares", methods=["GET"])
def get_fares():
    return jsonify(FARES)

@app.route("/ticket", methods=["POST"])
def issue_ticket():
    data = request.json

    # Validate zones
    start = data.get("start_zone")
    end = data.get("end_zone")
    if start not in ZONES or end not in ZONES:
        return jsonify({"success": False, "message": "Invalid zone selection."}), 400

    # Validate travellers
    travellers = data.get("travellers", {})
    for cat in FARES:
        if cat not in travellers:
            return jsonify({"success": False, "message": f"Missing {cat} travellers."}), 400
        if not isinstance(travellers[cat], int) or travellers[cat] < 0:
            return jsonify({"success": False, "message": f"Invalid quantity for {cat}."}), 400

    zones = calculate_zones(start, end)
    total_cost = sum(calculate_fare(zones, FARES[cat], qty) for cat, qty in travellers.items())

    voucher = generate_voucher(start, end, travellers, total_cost)
    return jsonify({"success": True, "voucher": voucher})

# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(debug=True)
