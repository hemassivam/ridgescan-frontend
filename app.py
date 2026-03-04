import os
import requests
from flask import Flask, render_template, request, jsonify

app     = Flask(__name__)
API_URL = os.environ.get('API_URL', 'http://localhost:8000').rstrip('/')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    try:
        resp = requests.post(
            f'{API_URL}/predict',
            files={'file': (file.filename, file.read(), file.content_type)},
            data={
                'name':   request.form.get('name', ''),
                'age':    request.form.get('age', ''),
                'gender': request.form.get('gender', ''),
                'email':  request.form.get('email', ''),
            },
            timeout=120
        )
        # Always return JSON — even if API errored
        try:
            return jsonify(resp.json()), resp.status_code
        except Exception:
            return jsonify({'error': f'API returned non-JSON. Status: {resp.status_code}. Body: {resp.text[:300]}'}), 502

    except requests.exceptions.ConnectionError:
        return jsonify({'error': f'Cannot reach API at {API_URL}. Check API_URL env var on Render.'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': 'API timed out. Model may still be loading — try again in 30 seconds.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def api_history():
    try:
        resp = requests.get(f'{API_URL}/history', timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<rid>', methods=['DELETE'])
def delete_record(rid):
    try:
        resp = requests.delete(f'{API_URL}/history/{rid}', timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    try:
        resp = requests.delete(f'{API_URL}/history/clear', timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
