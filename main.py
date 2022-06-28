from flask import Flask, render_template, request
from decrypt import start

app = Flask(__name__, template_folder='template')
app.config["SESSION_PERMANENT"] = True
app.config['UPLOAD_FOLDER'] = './'
app.config['MAX_CONTENT_PATH'] = 50*1024*1024


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        if not '.saz' in f.filename:
            return "<center><b>INVALID FILE EXTENSION!!</b></center>"
        decrypted_data = start(f.filename[:-4], f.filename, request.form['key'])
        return str(decrypted_data)
    else:
        return render_template('upload.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="4444")
