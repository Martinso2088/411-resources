import os
import time
from flask import Flask, make_response, request

app = Flask(__name__)

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

@app.route('/repeat', methods=['GET'])
def repeat():
    input_value = request.args.get('input', '')
    response = make_response(
        {
            'body': input_value,
            'status': 200
        }
    )
    return response

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'body' : 'OK',
            'status' : 200
        }
    )
    return response

@app.route('/hang')
def hang():
    while True:
        time.sleep(1)

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=False)
