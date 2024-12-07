# app.py
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import numpy as np
import joblib
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Load trained model and scaler
model = joblib.load('random_forest_model.joblib')
encoder = joblib.load('encoder.joblib')
scaler = joblib.load('scaler.joblib')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def predict_from_df(df):
    # Process categorical features
    categorical_features = ['jenis_kelamin', 'pemilik_mobil', 'pemilik_properti', 'jenis_pendapatan', 'pendidikan', 'status_perkawinan', 'jenis_rumah']
    input_encoded = encoder.transform(df[categorical_features])
    
    # Process numeric features
    numeric_features = ['usia', 'pendapatan_tahunan', 'pengalaman_kerja']
    input_scaled = scaler.transform(df[numeric_features])
    
    # Combine processed features
    input_processed = np.hstack((input_encoded, input_scaled))
    
    # Make prediction
    predictions = model.predict(input_processed)
    probabilities = model.predict_proba(input_processed)[:, 1]
    
    return predictions, probabilities

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from form
        data = {
            'jenis_kelamin': request.form['jenis_kelamin'],
            'pemilik_mobil': request.form['pemilik_mobil'],
            'pemilik_properti': request.form['pemilik_properti'],
            'anak': int(request.form['anak']),
            'pendapatan_tahunan': float(request.form['pendapatan_tahunan']),
            'jenis_pendapatan': request.form['jenis_pendapatan'],
            'pendidikan': request.form['pendidikan'],
            'status_perkawinan': request.form['status_perkawinan'],
            'jenis_rumah': request.form['jenis_rumah'],
            'usia': int(request.form['usia']),
            'pengalaman_kerja': int(request.form['pengalaman_kerja']),
            'telepon_seluler': int(request.form['telepon_seluler']),
            'telepon_kerja': int(request.form['telepon_kerja']),
            'telepon': int(request.form['telepon']),
            'ID_email': int(request.form['ID_email']),
            'anggota_keluarga': int(request.form['anggota_keluarga'])
        }
        
        df = pd.DataFrame([data])
        predictions, probabilities = predict_from_df(df)
        
        result = 'Disetujui' if predictions[0] == 1 else 'Ditolak'
        probability = probabilities[0]
        
        return render_template('result.html', hasil=result, probabilitas=probability, is_csv=False)
    
    return render_template('form.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('predict_csv', filename=filename))
    return render_template('upload.html')

@app.route('/predict_csv/<filename>')
def predict_csv(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file_path)
    
    predictions, probabilities = predict_from_df(df)
    
    df['Status'] = ['Disetujui' if p == 1 else 'Ditolak' for p in predictions]
    df['Probabilitas'] = probabilities * 100  # Convert to percentage
    
    # Use Pandas styling to create a more attractive table
    styled_df = df.style.set_table_attributes('class="table table-striped table-hover"')
    styled_df = styled_df.format({'Probabilitas': '{:.2f}%'})
    
    return render_template('result.html', 
                           table=styled_df.to_html(classes='table table-striped table-hover', index=False), 
                           titles=df.columns.values,
                           is_csv=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)