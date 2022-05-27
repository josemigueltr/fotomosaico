from flask import Flask, flash, request, redirect, url_for, render_template
from fotomosaico import fotomosaico
import os
from werkzeug.utils import secure_filename
import string
import random

app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

nombre_archivo_salida = ''
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    global nombre_archivo_salida

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No se ha seleccionado ninguna imagen.')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ruta = 'static/uploads/' + filename
        pixel = int(request.form['pixel'])
        letters = string.ascii_lowercase
        nombre_archivo_salida = ''.join(random.choice(letters) for i in range(8))
        salida = nombre_archivo_salida + ".jpg"
        fotomosaico(pixel, ruta, salida)
        flash('¡Se ha creado su fotomosaico!')
        return render_template('index.html', filename=salida)
    else:
        flash('Extensiones de archivo permitidas: png, jpg, jpeg')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run()