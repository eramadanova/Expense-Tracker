import pandas as pd
from flask import Blueprint, request, redirect, url_for
from .validators import validate_file, validate_columns, process_transaction
from app import db

import_bp = Blueprint('import_export', __name__)

@import_bp.route('/home-import', methods=['POST'])
def home_import():
    if request.method == 'POST':
        file = request.files.get('csv_file')

        if not validate_file(file):
            return redirect(url_for('home.home'))

        with file.stream as f:
            df = pd.read_csv(f)

        if not validate_columns(df):
            return redirect(url_for('home.home'))


        for index, row in df.iterrows():
            transaction = process_transaction(row, index)
            if transaction is not None:
                db.session.add(transaction)

        db.session.commit()

        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))

