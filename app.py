from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import jwt

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Make sure to set this in your .env file

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user = response.user
            # Store user ID and access token in session
            session['user_id'] = user.id
            session['access_token'] = response.session.access_token  # Store JWT token in session
            return redirect(url_for('account'))
        except AuthApiError as e:
            flash(f"Sign-in error: {e}", "error")
        except Exception as e:
            flash(f"Unexpected error: {e}", "error")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return redirect(url_for('login'))
        except AuthApiError as e:
            flash(f"Sign-up error: {e}", "error")
        except Exception as e:
            flash(f"Unexpected error: {e}", "error")
    return render_template('signup.html')

@app.route('/account')
def account():
    user_id = session.get('user_id')
    access_token = session.get('access_token')
    if not user_id or not access_token:
        flash("You need to log in to access your account.", "warning")
        return redirect(url_for('login'))

    try:
        # Decode JWT token to verify its validity
        decoded_token = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=['HS256'])
        locomotives = supabase.table('locomotives').select("*").eq('user_id', user_id).execute()
        return render_template('account.html', locomotives=locomotives.data)
    except jwt.ExpiredSignatureError as e:
        flash(f"JWT token has expired: {e}", "error")
    except jwt.DecodeError as e:
        flash(f"Error decoding JWT token: {e}", "error")
    except AuthApiError as e:
        flash(f"Error fetching user details: {e}", "error")
    except Exception as e:
        flash(f"Unexpected error: {e}", "error")

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    supabase.auth.sign_out()
    session.clear()
    return redirect(url_for('home'))

@app.route('/verify_token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return jsonify(decoded_token), 200
    except jwt.ExpiredSignatureError as e:
        return jsonify({"error": str(e)}), 400
    except jwt.DecodeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

