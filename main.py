from flask import Flask, request, render_template_string, jsonify
import threading
import time
import requests
import datetime

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>MAJNU POST SERVER</title>
    <link href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css' rel='stylesheet'>
    <link href='https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap' rel='stylesheet'>
    <style>
        body { background: #1a1a1a; color: #fff; min-height: 100vh; }
        .card { background: #2d2d2d; border: 1px solid #444; }
        .form-control { background: #333; color: #fff; border: 1px solid #555; }
        .glow {
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 10px #ff4444, 0 0 20px #ff0000;
        }
        #logBox { max-height: 300px; overflow-y: scroll; background: #111; padding: 10px; border: 1px solid #333; }
    </style>
    <script>
        setInterval(() => {
            fetch('/log')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('logBox').innerText = data.join("\\n");
                });
        }, 2000);

        function updateDelay() {
            const newDelay = document.getElementById('newDelay').value;
            fetch('/update_delay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ delay: newDelay })
            });
        }

        function stopPosting() {
            fetch('/stop', { method: 'POST' });
        }
    </script>
</head>
<body>
<div class='container py-5'>
    <div class='text-center mb-5'>
        <h1 class='glow'>MAJNU POST SERVER</h1>
        <h3 class='text-danger'>DARK WEB @ᴍᴀᴅᴇ ʙʏ ᴍᴀᴊɴᴜ</h3>
    </div>

    <div class='card mb-4'>
        <div class='card-body'>
            <form method='post' enctype='multipart/form-data'>
                <div class='form-group'>
                    <label>Post ID:</label>
                    <input type='text' name='threadId' class='form-control' required>
                </div>
                <div class='form-group'>
                    <label>Hater Name:</label>
                    <input type='text' name='kidx' class='form-control' required>
                </div>
                <div class='form-group'>
                    <label>Messages File:</label>
                    <input type='file' nane='messagesFile' class='form-control' accept='.txt' required>
                </div>
                <div class='form-group'>
                    <label>Tokens File:</label>
                    <input type='file' name='txtFile' class='form-control' accept='.txt' required>
                </div>
                <div class='form-group'>
                    <label>Speed (seconds):</label>
                    <input type='number' name='time' class='form-control' min='5' value='20' required>
                </div>
                <button type='submit' class='btn btn-danger btn-block'>Start Posting</button>
            </form>
        </div>
    </div>

    <div class='card mb-4'>
        <div class='card-body'>
            <h5>📡 Live Logs:</h5>
            <div id='logBox'></div>
            <div class='mt-3'>
                <label>Change Delay (seconds):</label>
                <input type='number' id='newDelay' class='form-control' placeholder='Enter new delay'>
                <button onclick='updateDelay()' class='btn btn-sm btn-info mt-2'>Update Delay</button>
                <button onclick='stopPosting()' class='btn btn-sm btn-warning mt-2 ml-2'>🛑 Stop Posting</button>
            </div>
        </div>
    </div>

    <div class='card'>
        <div class='card-body'>
            <form method='post' action='/check_tokens' enctype='multipart/form-data'>
                <label>🔍 Check Token Health:</label>
                <input type='file' name='txtFile' class='form-control' accept='.txt' required>
                <button type='submit' class='btn btn-sm btn-success mt-2'>Check Tokens</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""

log_output = []
runtime_delay = {"value": 20}
stop_event = threading.Event()

def post_comments(thread_id, hater_name, tokens, messages):
    log_output.append(f"[⏱️] Started at {datetime.datetime.now().strftime('%H:%M:%S')}")
    i = 0
    while not stop_event.is_set():
        msg = messages[i % len(messages)].strip()
        token = tokens[i % len(tokens)].strip()
        comment = f"{hater_name} {msg}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        url = f"https://graph.facebook.com/{thread_id}/comments"
        data = {"message": comment, "access_token": token}

        try:
            r = requests.post(url, headers=headers, data=data)
            if r.status_code == 200:
                log_output.append(f"[✅] Sent: {comment}")
            else:
                log_output.append(f"[❌] Failed: {comment} => {r.text}")
        except Exception as e:
            log_output.append(f"[⚠️] Error: {e}")

        i += 1
        time.sleep(runtime_delay["value"])

    log_output.append(f"[🛑] Posting stopped at {datetime.datetime.now().strftime('%H:%M:%S')}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        thread_id = request.form['threadId']
        hater_name = request.form['kidx']
        delay = int(request.form['time'])
        runtime_delay["value"] = delay
        tokens = request.files['txtFile'].read().decode('utf-8').splitlines()
        messages = request.files['messagesFile'].read().decode('utf-8').splitlines()
        stop_event.clear()
        threading.Thread(target=post_comments, args=(thread_id, hater_name, tokens, messages)).start()
    return render_template_string(HTML_PAGE)

@app.route('/log')
def log():
    return jsonify(log_output[-100:])

@app.route('/update_delay', methods=['POST'])
def update_delay():
    data = request.get_json()
    try:
        new_delay = int(data.get('delay'))
        runtime_delay['value'] = new_delay
        log_output.append(f"[⚙️] Delay updated to {new_delay} sec")
    except:
        pass
    return ('', 204)

@app.route('/stop', methods=['POST'])
def stop():
    stop_event.set()
    log_output.append("[🔴] Manual stop triggered.")
    return ('', 204)

@app.route('/check_tokens', methods=['POST'])
def check_tokens():
    tokens = request.files['txtFile'].read().decode('utf-8').splitlines()
    log_output.append("[🔍] Token check started...")
    for i, token in enumerate(tokens):
        url = "https://graph.facebook.com/me"
        params = {"access_token": token}
        try:
            r = requests.get(url, params=params)
            if r.status_code == 200 and "id" in r.json():
                name = r.json().get("name", "Unknown")
                log_output.append(f"[✅] Valid Token {i+1}: {name}")
            else:
                log_output.append(f"[❌] Invalid Token {i+1}")
        except Exception as e:
            log_output.append(f"[⚠️] Error on token {i+1}: {e}")
        time.sleep(0.5)
    log_output.append("[✅] Token check completed.")
    return ('', 204)

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8000)
