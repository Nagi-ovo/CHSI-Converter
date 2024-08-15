from flask import Flask, render_template
from utils import CHSIConverter
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def handle_convert():
    return CHSIConverter.convert_file()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(debug=True, port=port, host='0.0.0.0')
else:
    application = app