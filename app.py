from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
import os
import requests
import qrcode
import io
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib

app = Flask(__name__)
app.secret_key = os.urandom(24)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Import config (or use environment variables)
try:
    from config import OPENWEATHER_API_KEY, EMAIL_ADDRESS, EMAIL_PASSWORD
except ImportError:
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'c2e74fbea1196a95b90987b0694d735b')
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'janustheq@gmail.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'lvrnxpfntslitjhs')

# FastAPI Wellness Tracker URL
FASTAPI_URL = 'http://localhost:8001'

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', '635907166331-72cfhmu1q7jgsfcfqjli9mq60lck1mg3.apps.googleusercontent.com'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', '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'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('login'))


@app.route('/weather')
def weather():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('weather.html', user=session['user'])

@app.route('/jokes')
def jokes():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('jokes.html', user=session['user'])


@app.route('/encrypt')
def encrypt():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('encrypt.html', user=session['user'])


@app.route('/wellness')
def wellness():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('wellness.html', user=session['user'])

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

# Wellness Tracker Proxy Routes (Forward to FastAPI)
@app.route('/api/wellness/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def wellness_proxy(path):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        user_email = session['user']['email']
        url = f"{FASTAPI_URL}/api/{path}"

        if request.method == 'GET':
            params = dict(request.args)
            params['user_email'] = user_email
            response = requests.get(url, params=params, timeout=10)
        else:
            data = request.get_json() or {}
            data['user_email'] = user_email

            if request.method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif request.method == 'PUT':
                response = requests.put(url, json=data, timeout=10)
            elif request.method == 'DELETE':
                response = requests.delete(url, json=data, timeout=10)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify(
            {'error': 'Wellness Tracker service is not running. Please start the FastAPI server on port 8001'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/encrypt-text', methods=['POST'])
def encrypt_text():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    text = data.get('text', '')
    ciphers = data.get('ciphers', [])
    shift = data.get('shift', 3)
    keyword = data.get('keyword', '')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    if not ciphers:
        return jsonify({'error': 'Please select at least one cipher'}), 400

    try:
        results = []

        # Apply each cipher separately to the original text
        for cipher in ciphers:
            if cipher == 'atbash':
                encrypted_text = atbash_cipher(text)
                results.append({
                    'cipher': 'Atbash',
                    'description': 'Reverses the alphabet',
                    'encrypted_text': encrypted_text
                })

            elif cipher == 'caesar':
                encrypted_text = caesar_cipher(text, shift)
                results.append({
                    'cipher': 'Caesar',
                    'description': f'Shift by {shift}',
                    'encrypted_text': encrypted_text
                })

            elif cipher == 'vigenere':
                if not keyword:
                    return jsonify({'error': 'Keyword required for Vigenere cipher'}), 400
                encrypted_text = vigenere_cipher(text, keyword)
                results.append({
                    'cipher': 'Vigenere',
                    'description': f'Keyword: {keyword}',
                    'encrypted_text': encrypted_text
                })

        return jsonify({
            'success': True,
            'original_text': text,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def atbash_cipher(text):
    result = []
    for char in text:
        if char.isupper():
            result.append(chr(90 - (ord(char) - 65)))
        elif char.islower():
            result.append(chr(122 - (ord(char) - 97)))
        else:
            result.append(char)
    return ''.join(result)


def caesar_cipher(text, shift):
    result = []
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) - 97 + shift) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)


def vigenere_cipher(text, keyword):
    result = []
    keyword = keyword.upper()
    keyword_index = 0

    for char in text:
        if char.isalpha():
            shift = ord(keyword[keyword_index % len(keyword)]) - 65
            if char.isupper():
                result.append(chr((ord(char) - 65 + shift) % 26 + 65))
            else:
                result.append(chr((ord(char) - 97 + shift) % 26 + 97))
            keyword_index += 1
        else:
            result.append(char)

    return ''.join(result)

@app.route('/api/joke', methods=['GET'])
def get_joke():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get joke from JokeAPI
        response = requests.get('https://v2.jokeapi.dev/joke/Any?safe-mode', timeout=10)

        if response.status_code == 200:
            joke_data = response.json()

            if joke_data['type'] == 'single':
                joke_text = joke_data['joke']
            else:
                joke_text = f"{joke_data['setup']}\n\n{joke_data['delivery']}"

            return jsonify({
                'success': True,
                'joke': joke_text,
                'category': joke_data.get('category', 'General')
            })
        else:
            return jsonify({'error': 'Failed to fetch joke'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            'success': True,
            'qr_code': f'data:image/png;base64,{img_base64}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/send-joke-email', methods=['POST'])
def send_joke_email():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    recipient_email = data.get('email', '')
    joke_text = data.get('joke', '')
    include_qr = data.get('include_qr', False)
    qr_image = data.get('qr_image', '')

    if not recipient_email or not joke_text:
        return jsonify({'error': 'Email and joke are required'}), 400

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = '😂 Your Daily Joke from IntegrativeHub!'

        # Email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #1e88e5; text-align: center;">😂 Joke of the Day!</h2>
                    <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; font-size: 16px; line-height: 1.6;">
                        {joke_text.replace(chr(10), '<br>')}
                    </div>
                    <p style="text-align: center; color: #666; margin-top: 30px;">
                        Sent with ❤️ from IntegrativeHub<br>
                        <small>Powered by {session['user']['name']}</small>
                    </p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Attach QR code if requested
        if include_qr and qr_image:
            # Extract base64 data
            qr_data = qr_image.split(',')[1]
            qr_bytes = base64.b64decode(qr_data)

            image = MIMEImage(qr_bytes, name='joke_qr.png')
            image.add_header('Content-ID', '<qr_image>')
            msg.attach(image)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({
            'success': True,
            'message': 'Email sent successfully!'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500


@app.route('/api/send-encrypted-email', methods=['POST'])
def send_encrypted_email():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    recipient_email = data.get('email', '')
    encrypted_text = data.get('encrypted_text', '')
    cipher_name = data.get('cipher_name', '')
    cipher_description = data.get('cipher_description', '')
    include_qr = data.get('include_qr', False)
    qr_image = data.get('qr_image', '')

    if not recipient_email or not encrypted_text:
        return jsonify({'error': 'Email and encrypted text are required'}), 400

    # Check if email is configured
    if EMAIL_ADDRESS == 'YOUR_EMAIL@gmail.com' or EMAIL_PASSWORD == 'YOUR_APP_PASSWORD':
        return jsonify({'error': 'Please configure email settings in app.py (EMAIL_ADDRESS and EMAIL_PASSWORD)'}), 500

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = f'🔒 Encrypted Message ({cipher_name} Cipher) from IntegrativeHub'

        # Email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #e91e63; text-align: center;">🔒 Encrypted Message</h2>
                    <div style="background: #fce4ec; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center;">
                        <span style="background: #e91e63; color: white; padding: 8px 20px; border-radius: 20px; font-weight: 600;">
                            {cipher_name} Cipher
                        </span>
                        <p style="margin: 10px 0 0 0; color: #666;">{cipher_description}</p>
                    </div>
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; font-family: monospace; font-size: 16px; line-height: 1.6; word-wrap: break-word;">
                        {encrypted_text}
                    </div>
                    <p style="text-align: center; color: #666; margin-top: 30px;">
                        Sent with ❤️ from IntegrativeHub<br>
                        <small>Powered by {session['user']['name']}</small>
                    </p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Attach QR code if requested
        if include_qr and qr_image:
            # Extract base64 data
            qr_data = qr_image.split(',')[1]
            qr_bytes = base64.b64decode(qr_data)

            image = MIMEImage(qr_bytes, name='encrypted_qr.png')
            image.add_header('Content-ID', '<qr_image>')
            msg.attach(image)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({
            'success': True,
            'message': 'Email sent successfully!'
        })
    except smtplib.SMTPAuthenticationError as e:
        return jsonify({
                           'error': 'Gmail authentication failed. Please use an App Password. See: https://support.google.com/accounts/answer/185833'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@app.route('/api/weather', methods=['POST'])
def get_weather():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    city = data.get('city', '')

    if not city:
        return jsonify({'error': 'City name is required'}), 400

    try:
        # Get weather data from OpenWeatherMap
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY  }&units=metric'
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            weather_data = response.json()
            return jsonify({
                'success': True,
                'city': weather_data['name'],
                'country': weather_data['sys']['country'],
                'temperature': round(weather_data['main']['temp']),
                'feels_like': round(weather_data['main']['feels_like']),
                'description': weather_data['weather'][0]['description'].title(),
                'humidity': weather_data['main']['humidity'],
                'wind_speed': round(weather_data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'pressure': weather_data['main']['pressure'],
                'icon': weather_data['weather'][0]['icon'],
                'lat': weather_data['coord']['lat'],
                'lon': weather_data['coord']['lon']
            })
        elif response.status_code == 404:
            return jsonify({'error': 'City not found'}), 404
        else:
            return jsonify({'error': 'Failed to fetch weather data'}), 500
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout. Please try again'}), 500
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")  # Debug log
        return jsonify({'error': 'Network error. Please check your connection'}), 500
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/accounts/google/login/callback/')
def authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    session['user'] = {
        'email': user_info['email'],
        'name': user_info.get('name', 'User'),
        'picture': user_info.get('picture', '')
    }
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
