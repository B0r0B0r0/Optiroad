def get_contact_email(name, message):
    message_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Message Received</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            background-color: #ffffff;
            padding: 20px;
            margin: auto;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background-color: #007bff;
            color: #ffffff;
            padding: 10px;
            text-align: center;
            border-radius: 10px 10px 0 0;
            font-size: 22px;
        }}
        .content {{
            font-size: 16px;
            color: #333;
            padding: 20px 0;
        }}
        .message-box {{
            padding: 15px;
            font-size: 16px;
            color: #333;
            background: #f9f9f9;
            border-left: 5px solid #007bff;
            margin: 20px 0;
            white-space: pre-line;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #777;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">📢 Message Received!</div>
        <p><strong>Hello, {name}!</strong></p>
        <p class="content">
            Thank you for reaching out to us. We have received your message and one of our administrators 
            will review it shortly. Below is a copy of your message for your reference:
        </p>
        <div class="message-box">
            {message}
        </div>
        <p class="content">
            We will get back to you as soon as possible. If you need urgent assistance, please don't hesitate 
            to contact our support team.
        </p>
        <p class="footer">
            This email was generated automatically. Please do not reply.
        </p>
    </div>
</body>
</html>
"""
    return message_body

def get_key_email(name, key):
    message_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Key Delivery</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                background-color: #ffffff;
                padding: 20px;
                margin: auto;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #28a745;
                color: #ffffff;
                padding: 10px;
                text-align: center;
                border-radius: 10px 10px 0 0;
                font-size: 22px;
            }}
            .content {{
                font-size: 16px;
                color: #333;
                padding: 20px 0;
            }}
            .key-box {{
                padding: 15px;
                font-size: 16px;
                color: #333;
                background: #f9f9f9;
                border-left: 5px solid #28a745;
                margin: 20px 0;
                word-break: break-word;
            }}
            .footer {{
                text-align: center;
                font-size: 14px;
                color: #777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">🔑 Your Key is Here!</div>
            <p><strong>Hello, {name}!</strong></p>
            <p class="content">
                We are pleased to provide you with your key. Below is the key for your reference:
            </p>
            <div class="key-box">
                {key}
            </div>
            <p class="content">
                Please keep this key safe and do not share it with anyone. If you have any questions or concerns, 
                feel free to contact our support team.
            </p>
            <p class="footer">
                This email was generated automatically. Please do not reply.
            </p>
        </div>
    </body>
    </html>
    """
    return message_body