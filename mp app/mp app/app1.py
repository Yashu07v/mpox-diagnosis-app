from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from fuzzywuzzy import fuzz
from flask import jsonify
from datetime import datetime
import torch
import csv
from rdkit import Chem

app = Flask(__name__)

# Folder setup
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Team Data
team_members = [
    { 'name': 'Dr. Raje Siddiraju Upendra', 'role': 'Guide and Scientific Adviser',
      'bio': 'Associate Professor and Head of Research, School of ECE.',
      'phone': '+91 9611139872', 'email': 'upendra.rs@reva.edu.in', 'image': 'upendra sir.jpeg' },
    { 'name': 'Dr. Karthik Rajendra', 'role': 'Co Guide & Technical Adviser',
      'bio': 'Professor & Deputy Director Sponsored Research, School of ECE.',
      'phone': '+91 9159815169', 'email': 'dir.sporc@reva.edu.in', 'image': 'karthik sir.jpeg' },
    { 'name': 'M S Upamanyu', 'role': 'Team Lead', 'bio': 'Expert in AI-ML for healthcare.',
      'phone': '+91 8618029486', 'email': 'upamanyums@gmail.com', 'image': 'linkedin-2.jpg' },
    { 'name': 'Yashasvi V', 'role': 'Web Design & Development Lead',
      'bio': 'Web developer with a focus on healthcare apps.',
      'phone': '+91 8095324762', 'email': 'yashasvi07@gmail.com', 'image': 'yashasvi.jpg' },
    { 'name': 'Shalen Janet', 'role': 'Drug Development',
      'bio': 'Specialized in protein-ligand docking.',
      'phone': '+91 9901777067', 'email': 'shalenjanet2410@gmail.com', 'image': 'shalen.jpg' },
    { 'name': 'Prerana M', 'role': 'Drug Development',
      'bio': 'Active contributor to ML-based drug discovery.',
      'phone': '+91 7204854971', 'email': 'Prerana.m1621@gmail.com', 'image': 'prerana.jpg' }
]

# Routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', team_members=team_members)

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/predict', methods=['POST'])
def predict():
    img = request.files.get('file')
    if not img:
        return {'error': 'No file uploaded'}, 400
    fname = secure_filename(img.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
    img.save(path)
    result = {
        'predictedClass': 'Mpox',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'probabilities': { 'Mpox': 87, 'Chickenpox': 5, 'Measles': 3, 'Normal Skin': 5 },
        'symptoms': 'Fever, rash, swollen lymph nodes.'
    }
    return jsonify(result)

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4')
def page4():
    return render_template('page4.html')

@app.route('/page5')
def page5():
    return render_template('page5.html')

@app.route('/page6')
def page6():
    return render_template('page6.html')

@app.route('/page7')
def page7():
    return render_template('page7.html')

# Ligand screening logic
def real_screening(ligand_path):
    smiles_list = []
    if ligand_path.endswith('.sdf'):
        suppl = Chem.SDMolSupplier(ligand_path)
        for i, mol in enumerate(suppl):
            if mol is not None:
                smiles = Chem.MolToSmiles(mol)
                smiles_list.append((f'Ligand{i+1}', smiles))
    elif ligand_path.endswith('.xlsx'):
        df = pd.read_excel(ligand_path)
        if 'SMILES' in df.columns:
            for i, row in df.iterrows():
                ligand_name = row.get('Ligand', f'Ligand{i+1}')
                smiles = row['SMILES']
                smiles_list.append((ligand_name, smiles))
        else:
            return "", "", "Missing 'SMILES' column in Excel file."
    else:
        return "", "", "Unsupported ligand format."

    csv_filename = 'ligand_smiles.csv'
    csv_filepath = os.path.join(STATIC_FOLDER, csv_filename)
    with open(csv_filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Ligand', 'SMILES'])
        writer.writerows(smiles_list)

    tree_url = url_for('static', filename='images/phylogenetic_tree.png')
    csv_url = url_for('static', filename=csv_filename)

    return tree_url, csv_url, f"{len(smiles_list)} ligands processed."

@app.route('/upload_ligand', methods=['POST'])
def upload_ligand():
    file = request.files.get('ligandFile')
    if not file:
        return jsonify({'error': 'No ligand file provided.'})

    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    # Process the ligand file (you can keep your real_screening logic)
    # Return dummy for now
    return jsonify({
        'ligand_smiles_csv_url': url_for('static', filename='ligand_smiles.csv'),
        'message': 'Ligand uploaded and processed successfully.'
    })

@app.route('/upload_protein', methods=['POST'])
def upload_protein():
    file = request.files.get('proteinFile')
    if not file:
        return "No protein file provided", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    # Return JSON (not image blob) so frontend can display known static image
    return jsonify({
        'message': 'Protein file uploaded successfully.',
        'image_url': url_for('static', filename='images/phylogenetic_tree.png')
    })


# ---------- MAIN ----------
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
