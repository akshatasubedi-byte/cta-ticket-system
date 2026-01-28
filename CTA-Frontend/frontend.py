import requests

BASE_URL = "http://127.0.0.1:5000"

# ---------- VALIDATION ----------
def get_valid_zone(prompt):
    while True:
        try:
            zone = int(input(prompt))
            if zone in [1, 2, 3]:
                return zone
            print("Please select a valid zone (1-3).")
        except ValueError:
            print("Numeric input only.")

def get_valid_quantity(prompt):
    while True:
        try:
            qty = int(input(prompt))
            if qty >= 0:
                return qty
            print("Quantity cannot be negative.")
        except ValueError:
            print("Numeric input only.")

# ---------- FRONTEND LOGIC ----------
def login():
    attempts = 3
    while attempts > 0:
        username = input("Username: ")
        password = input("Password: ")
        try:
            response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
            data = response.json()
            if data.get("success"):
                print("Login successful.\n")
                return True
            else:
                attempts -= 1
                print(f"Invalid credentials. Attempts left: {attempts}")
        except requests.exceptions.ConnectionError:
            print("Backend not running. Please start the server.")
            return False
    print("Too many failed attempts. Session locked.")
    return False

def main():
    print("CTA Automated Ticketing System (Frontend)")

    if not login():
        return

    while True:
        print("\nZones:")
        print("1. Central")
        print("2. Midtown")
        print("3. Downtown")

        start = get_valid_zone("Boarding Zone: ")
        end = get_valid_zone("Destination Zone: ")

        travellers = {}
        for cat in ["Adult", "Child", "Student", "Senior"]:
            travellers[cat] = get_valid_quantity(f"{cat} travellers: ")

        # Send data to backend
        payload = {
            "start_zone": start,
            "end_zone": end,
            "travellers": travellers
        }

        try:
            response = requests.post(f"{BASE_URL}/ticket", json=payload)
            data = response.json()
            if data.get("success"):
                voucher = data.get("voucher")
                print("\n----- CTA TRAVEL VOUCHER -----")
                print(f"Date & Time: {voucher['date_time']}")
                print(f"Boarding Zone: {voucher['boarding_zone']}")
                print(f"Destination Zone: {voucher['destination_zone']}")
                print(f"Zones Travelled: {voucher['zones_travelled']}")
                for cat, qty in voucher['travellers'].items():
                    print(f"{cat}: {qty}")
                print(f"Total Travellers: {voucher['total_travellers']}")
                print(f"Total Cost: {voucher['total_cost']} credits")
                print("------------------------------\n")
            else:
                print("Error:", data.get("message"))
        except requests.exceptions.ConnectionError:
            print("Backend not running. Please start the server.")
            return

        again = input("Issue another ticket? (y/n): ").lower()
        if again != "y":
            print("Session ended.")
            break

if __name__ == "__main__":
    main()

