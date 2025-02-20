from flask import Flask, render_template, request, jsonify
import requests
import random
import time
import mysql.connector
from plyer import notification

app = Flask(__name__)

otp_store = {}


FAST2SMS_API_KEY = 'i6Hca0uVxLQLvjtV9EPapx8kfQa0oiMBcZ75f5NZ5OO2GOmw2Vc1aIuXl0VX'

def get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='Km@123456',
        database='user_transactions'
    )

def show_notification(title, message):
    """Display a desktop notification."""
    notification.notify(
        title=title,
        message=message,
        app_name='Transaction Alert',
        timeout=5 
    )

def get_user_details(card_number):
    """Retrieve user details based on card number."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM user_details WHERE cardNumber = %s"
    cursor.execute(query, (card_number,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def block_card(card_number):
    """Block a card by adding it to the 'blocked_cards' table."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO blocked_cards (cardNumber, reason) VALUES (%s, 'Incorrect details')"
    cursor.execute(query, (card_number,))
    connection.commit()
    cursor.close()
    connection.close()

def is_card_blocked(card_number):
    """Check if a card is blocked."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM blocked_cards WHERE cardNumber = %s"
    cursor.execute(query, (card_number,))
    result = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return result > 0

def get_blocked_cards():
    """Retrieve all blocked cards."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT cardNumber, reason FROM blocked_cards"
    cursor.execute(query)
    cards = cursor.fetchall()
    cursor.close()
    connection.close()
    return cards

def unblock_card(card_number):
    """Unblock a card by removing it from the 'blocked_cards' table."""
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM blocked_cards WHERE cardNumber = %s"
    cursor.execute(query, (card_number,))
    connection.commit()
    cursor.close()
    connection.close()

# Flask routes
@app.route('/')
def index():
    return render_template('PROJ.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/blocked-cards')
def blocked_cards():
    cards = get_blocked_cards()
    return jsonify(cards)

@app.route('/admin/unblock-card', methods=['POST'])
def admin_unblock_card():
    data = request.json
    card_number = data.get('cardNumber')
    if not card_number:
        return jsonify({'message': 'Card number is required.'}), 400
    unblock_card(card_number)
    return jsonify({'message': f'Card {card_number} has been unblocked successfully.'}), 200

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    phone_number = data.get('phoneNumber')

    if not phone_number:
        return jsonify({'message': 'Phone number is required.'}), 400

    otp = random.randint(100000, 999999)
    timestamp = time.time()
    otp_store[phone_number] = (otp, timestamp)

    message = f'Your OTP is {otp}. It is valid for 5 minutes.'
    url = (
        f"https://www.fast2sms.com/dev/bulkV2?"
        f"authorization={FAST2SMS_API_KEY}&"
        f"route=otp&flash=0&numbers={phone_number}&variables_values={otp}"
    )

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify({'message': 'OTP sent successfully!'}), 200
        else:
            return jsonify({'message': 'Failed to send OTP.', 'details': response.text}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Error while sending OTP: {str(e)}'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone_number = data.get('phoneNumber')
    user_otp = data.get('otp')

    if not phone_number or not user_otp:
        return jsonify({'message': 'Phone number and OTP are required.'}), 400

    if phone_number in otp_store:
        saved_otp, timestamp = otp_store[phone_number]
        current_time = time.time()
        if saved_otp == int(user_otp) and current_time - timestamp <= 300:
            del otp_store[phone_number]
            return jsonify({'message': 'OTP verified successfully!'}), 200
        else:
            return jsonify({'message': 'Invalid or expired OTP.'}), 400
    else:
        return jsonify({'message': 'OTP not found.'}), 404

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.json
    card_number = data.get('cardNumber')
    card_holder_name = data.get('cardHolderName')
    cvv = data.get('cvv')
    phone_number = data.get('phoneNumber')
    location = data.get('location')

    phone_codes = {
        "India": "+91", "United States": "+1", "Canada": "+1",
        "Australia": "+61", "United Kingdom": "+44", "Germany": "+49",
        "France": "+33", "Japan": "+81", "China": "+86", "Brazil": "+55"
    }

    code = phone_codes.get(location, "")
    phone_number = code + str(phone_number)

    if is_card_blocked(card_number):
        show_notification("Transaction Blocked", "This card is blocked.")
        return jsonify({'message': 'This card is blocked. Contact support.'}), 403


    user_details = get_user_details(card_number)
    if user_details:
        if (user_details['cardHolderName'] == card_holder_name and
            user_details['cvv'] == cvv and
            user_details['phoneNumber'] == phone_number and
            user_details['location'] == location):
            show_notification("Transaction Secure", "User details match.")
            return jsonify({'message': 'Transaction is secure.'}), 200
        else:
            block_card(card_number)
            show_notification("Transaction Warning", "Incorrect details. Card blocked.")
            return jsonify({'message': 'Incorrect details! Card has been blocked.'}), 403
    else:
        show_notification("Transaction Warning", "User not found.")
        return jsonify({'message': 'User not found.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)