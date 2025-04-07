from flask import Flask, request, jsonify  
import os  
import requests  
import smtplib  # For sending emails  

app = Flask(__name__)  

# --- Configuration ---  
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")  
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")  # Your email address  
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # Your email password (or app password if using Gmail)  
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT") # Recipient email for alerts  


# --- Priority Keywords ---  
HIGH_PRIORITY_KEYWORDS = ["urgent", "critical", "down", "error", "immediately", "escalate"]  
LOW_PRIORITY_KEYWORDS = ["lunch", "reminder", "fyi", "meeting", "update"]  

def check_priority(message_text):  
    """ Check the priority of the message. """  
    message_lower = message_text.lower()  
    if any(keyword in message_lower for keyword in HIGH_PRIORITY_KEYWORDS):  
        return "High"  
    elif any(keyword in message_lower for keyword in LOW_PRIORITY_KEYWORDS):  
        return "Low"  
    else:  
        return "Medium"  

def send_email_alert(message_text):  
    """Send an email alert for high priority messages."""  
    try:  
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Adjust for your email provider  
        server.starttls()  
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)  
        subject = "PriorityPing - High Priority Alert!"  
        body = f"High Priority Slack Message Detected:\n\n{message_text}\n\nCheck Slack for details."  
        message = f"Subject: {subject}\n\n{body}"  
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, message)  
        print("Email alert sent!")  
    except Exception as e:  
        print(f"Error sending email: {e}")  
    finally:  
        if 'server' in locals() and server:  
            server.quit()  

def respond_in_thread(channel_id, thread_ts, message):  
    """Respond in a Slack thread."""  
    headers = {  
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',  
        'Content-Type': 'application/json'  
    }  
    payload = {  
        'channel': channel_id,  
        'thread_ts': thread_ts,  
        'text': message  
    }  
    response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)  
    if response.status_code != 200:  
        print(f"Error responding in thread: {response.status_code} - {response.text}")  

@app.route('/process_message', methods=['POST'])  
def process_message():  
    """Process incoming messages."""  
    data = request.get_json()  
    if not data or 'text' not in data:  
        return jsonify({"error": "Invalid request"}), 400  

    message_text = data['text']  
    priority = check_priority(message_text)  
    print(f"Message: '{message_text}', Priority: {priority}")  

    if priority == "High":  
        send_email_alert(message_text)  # Send email alert for high-priority messages  

    return jsonify({"priority": priority, "message": message_text}), 200  

@app.route('/slack/events', methods=['POST'])  
def slack_events():  
    """Handle Slack events."""  
    data = request.get_json()  

    if data['type'] == 'url_verification':  
        return jsonify({'challenge': data['challenge']}), 200  

    if data['type'] == 'event_callback':  
        event = data['event']  
        if event['type'] == 'message' and 'subtype' not in event:  
            message_text = event['text']  
            channel_id = event['channel']  
            user_id = event['user']  

            user_info = get_slack_user_info(user_id)  
            channel_info = get_slack_channel_info(channel_id)  
            sender_name = user_info.get('name', 'Unknown User')  
            channel_name = channel_info.get('name', 'Unknown Channel')  

            print(f"Received message from {sender_name} in #{channel_name}: '{message_text}'")  

            priority = check_priority(message_text)  
            print(f"Priority: {priority}")  

            if priority == "High":  
                send_email_alert(f"#{channel_name} - {sender_name}: {message_text}")  # Send email alert  
                respond_in_thread(  
                    channel_id, event['ts'],   
                    ":bangbang: **High Priority Alert Detected!** :bangbang: This message has been flagged as high priority and an email alert has been sent."  
                )  # Respond in thread  

    return jsonify({"success": True}), 200  

def get_slack_user_info(user_id):  
    """Fetch user information from Slack (dummy implementation)."""  
    # Replace this with actual API call to Slack  
    return {"name": "Test User"}  

def get_slack_channel_info(channel_id):  
    """Fetch channel information from Slack (dummy implementation)."""  
    # Replace this with actual API call to Slack  
    return {"name": "Test Channel"}  

@app.route('/')  # Home route  
def home():  
    return "PriorityPing is running (Slack & Email Only)!"  

if __name__ == '__main__':  
    app.run(debug=True)  