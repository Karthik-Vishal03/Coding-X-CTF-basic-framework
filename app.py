from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define the challenges with their respective test cases and solutions
challenges = [
    {
        "id": 1,
        "question": "Write a function that returns the square of a number.(Define the name of your function as 'square')",
        "function_name": "square",
        "test_cases": [2, 3, 4],
        "expected_results": [4, 9, 16],
        "character": "TVRDIG"
    },
    {
        "id": 2,
        "question": "Write a function that returns True if a number is even, else False.(Define the name of your function as 'is_even')",
        "function_name": "is_even",
        "test_cases": [2, 3, 4],
        "expected_results": [True, False, True],
        "character": "lzIHRoZS"
    },
    {
        "id": 3,
        "question": "Write a function that returns the reverse of a string. (Define the name of your function as 'reverse_string')",
        "function_name": "reverse_string",
        "test_cases": ["hello", "world", "python"],
        "expected_results": ["olleh", "dlrow", "nohtyp"],
        "character": "BiZXN0"
    }
]

# Helper functions to interact with the SQLite database
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS progress
                        (user_id INTEGER, challenge_id INTEGER, character TEXT)''')

def get_user_id(username):
    with sqlite3.connect('database.db') as conn:
        user = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
    return user[0] if user else None

def get_user_progress(user_id):
    with sqlite3.connect('database.db') as conn:
        progress = conn.execute('SELECT challenge_id, character FROM progress WHERE user_id=?', (user_id,)).fetchall()
    return progress

init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = get_user_id(session['username'])
    progress = get_user_progress(user_id)
    completed_challenges = [p[0] for p in progress]
    collected_characters = ''.join([p[1] for p in progress])
    return render_template('index.html', challenges=challenges, completed_challenges=completed_challenges, collected_characters=collected_characters)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge(challenge_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = get_user_id(session['username'])
    challenge = next((ch for ch in challenges if ch["id"] == challenge_id), None)
    if request.method == 'POST':
        user_code = request.form.get("code")
        function_name = challenge["function_name"]

        try:
            compiled_code = compile(user_code, '<string>', 'exec')
            exec_locals = {}
            exec(compiled_code, {}, exec_locals)

            function = exec_locals.get(function_name)
            if not function:
                flash(f"Function '{function_name}' not found in your code.", 'error')
                return redirect(request.url)
                
            for test_input, expected_result in zip(challenge["test_cases"], challenge["expected_results"]):
                result = function(test_input)
                if result != expected_result:
                    flash(f'Test failed for input {test_input}. Expected {expected_result}, got {result}.', 'error')
                    return redirect(request.url)
            
            with sqlite3.connect('database.db') as conn:
                conn.execute('INSERT INTO progress (user_id, challenge_id, character) VALUES (?, ?, ?)', (user_id, challenge_id, challenge["character"]))
            
            flash(f'Challenge {challenge_id} passed! You have unlocked the key: {challenge["character"]}. Keep solving more to find more!', 'success')
            return redirect(url_for('index'))

        except SyntaxError as e:
            flash(f'SyntaxError in your code: {e}', 'error')
        except Exception as e:
            flash(f'Error executing code: {e}', 'error')
        
        return redirect(request.url)

    return render_template('challenge.html', challenge=challenge)

@app.route('/final', methods=['GET', 'POST'])
def final():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = get_user_id(session['username'])
    progress = get_user_progress(user_id)
    collected_characters = ''.join([p[1] for p in progress])
    
    if len(progress) < len(challenges):
        flash('Complete all the challenges first', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        final_answer = request.form['final_answer']
        try:
            decoded_answer = final_answer
            if decoded_answer.strip() == 'MTC is the best':
                return render_template('congratulations.html')
            else:
                flash('Incorrect final answer.', 'error')
        except Exception as e:
            flash(f'Error decoding final answer: {str(e)}', 'error')

    return render_template('final.html', collected_characters=collected_characters)

if __name__ == '__main__':
    app.run(debug=True)
