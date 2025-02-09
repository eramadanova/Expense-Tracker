"""
    Defines report-related routes for generating and exporting financial reports.
"""

import csv
import io
from flask import render_template, Blueprint, request, redirect, url_for, Response, flash
from typing import Dict, List, Optional, Union
from werkzeug.wrappers import Response as WerkzeugResponse
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import src.config as config
from src.utils import (
    get_categories,
    get_transactions,
    get_transactions_by_type
)
from src.models import Transaction

report_bp = Blueprint('report', __name__)

def filter_by_category(filter_type: str, arguments: Dict[str, Optional[str]]) -> List[Transaction]:
    """
    Filters transactions based on the given criteria.

    :param filter_type: Type of filtering ('date', 'amount', 'category').
    :param arguments: Dictionary containing filter values.
    :return: List of filtered transactions.
    """
    transactions = get_transactions()
    filtered_transactions = []

    if filter_type == 'date':
        from_date = arguments['from_date']
        to_date = arguments['to_date']
        if from_date is not None and to_date is not None:
            filtered_transactions = [transaction for transaction in transactions
                                     if from_date <= transaction.date <= to_date]

    elif filter_type == 'amount':
        filter_amount = arguments['filter_amount']
        if filter_amount is not None:
            try:
                filter_amount = float(filter_amount)
                filtered_transactions = [ transaction for transaction in transactions
                                         if float(f"{transaction.amount:.2f}") == filter_amount]
            except ValueError:
                flash('Invalid amount', 'danger')

    elif filter_type == 'category':
        filter_category = arguments['filter_category']
        if filter_category is not None:
            try:
                filter_category = int(filter_category)
                filtered_transactions = [transaction for transaction in transactions
                                         if transaction.category_id == filter_category]
            except ValueError:
                pass

    return filtered_transactions

@report_bp.route('/report', methods=['GET'])
def report() -> str:
    """
    Renders the report page with transaction filters.

    :return: Rendered report template.
    """
    categories = get_categories()
    filter_type = request.args.get('filter_type')
    filtered_transactions = filter_by_category(filter_type, request.args)
    return render_template('report.html',
                           categories=categories,
                           filtered_transactions=filtered_transactions,
                           default_currency=config.DEFAULT_CURRENCY)

def generate_csv(transactions: List[Transaction]) -> Response:
    """
    Generates a CSV file from transactions.

    :param transactions: List of transaction objects.
    :return: Flask response containing the CSV file.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['date', 'category', 'description', 'amount', 'currency'])

    for transaction in transactions:
        writer.writerow([transaction.date, transaction.category.name, transaction.description,
                         f"{transaction.amount:.2f}", config.DEFAULT_CURRENCY])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers['Content-Disposition'] = 'attachment; filename=report.csv'

    return response

def generate_pdf(transactions: List[Transaction]) -> Response:
    """
    Generates a PDF report of transactions.

    :param transactions: List of transaction objects.
    :return: Flask response containing the PDF file.
    """
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle('Transaction Report')

    y_position = 750
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(230, y_position, 'Transaction Report')
    y_position -= 30

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_position, 'Date')
    pdf.drawString(130, y_position, 'Category')
    pdf.drawString(250, y_position, 'Description')
    pdf.drawString(400, y_position, 'Amount')
    pdf.drawString(500, y_position, 'Currency')
    y_position -= 20

    pdf.setFont("Helvetica", 10)
    for transaction in transactions:
        if y_position < 50:
            pdf.showPage()
            y_position = 750

        pdf.drawString(50, y_position, str(transaction.date))
        pdf.drawString(130, y_position, transaction.category.name)
        pdf.drawString(250, y_position, transaction.description)
        pdf.drawString(400, y_position, f"{transaction.amount:.2f}")
        pdf.drawString(500, y_position, config.DEFAULT_CURRENCY)
        y_position -= 20

    pdf.save()
    output.seek(0)

    response = Response(output.getvalue(), mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response

def generate_pie_chart(filtered_transactions: List[Transaction]) -> Response:
    """
    Generates a pie chart for filtered transactions.

    :param filtered_transactions: List of transactions for the chart.
    :return: Flask response containing the pie chart image.
    """
    category_totals = {}

    for transaction in filtered_transactions:
        category_name = transaction.category.name
        if category_name in category_totals:
            category_totals[category_name] += transaction.amount
        else:
            category_totals[category_name] = transaction.amount

    labels = category_totals.keys()
    sizes = category_totals.values()
    colors = get_cmap('Paired')(range(len(labels)))

    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')

    output = io.BytesIO()
    plt.savefig(output, format='png')
    plt.close()
    output.seek(0)

    response = Response(output.getvalue(), content_type='image/png')
    response.headers['Content-Disposition'] = 'attachment; filename=pie_chart.png'

    return response

def get_filtered_transactions(filtered_transaction_ids_str: str) -> List[Transaction]:
    """
    Retrieves transactions based on a list of transaction IDs.

    :param filtered_transaction_ids_str: Comma-separated string of transaction IDs.
    :return: List of filtered transaction objects.
    """
    try:
        filtered_transaction_ids = [int(id) for id in filtered_transaction_ids_str.split(',')]
    except ValueError:
        filtered_transaction_ids = []

    transactions = get_transactions()
    return [transaction for transaction in transactions
            if transaction.id in filtered_transaction_ids]

@report_bp.route('/report-table', methods=['POST'])
def report_table() -> Union[Response, WerkzeugResponse, str]:
    """
    Exports transactions as a PDF or CSV file based on user selection.

    :return: Flask response with the exported file.
    """
    if request.method == 'POST':
        filtered_transaction_ids_str = request.form['filtered_transaction_ids']
        filtered_transactions = get_filtered_transactions(filtered_transaction_ids_str)
        export_type = request.form['export_type']

        if export_type == 'pdf':
            return generate_pdf(filtered_transactions)
        if export_type == 'csv':
            return generate_csv(filtered_transactions)

        return redirect(url_for('report.report'))

    return redirect(url_for('report.report'))

@report_bp.route('/report-chart', methods=['POST'])
def report_chart() -> Union[Response, WerkzeugResponse, str]:
    """
    Generates and returns a pie chart for either income or expense transactions.

    :return: Flask response with the chart image.
    """
    if request.method == 'POST':
        filtered_transaction_ids_str = request.form['filtered_transaction_ids']
        filtered_transactions = get_filtered_transactions(filtered_transaction_ids_str)
        chart_type = request.form['chart_type']

        if chart_type == 'pie_expense':
            filtered_transactions = get_transactions_by_type(filtered_transactions, 'expense')
            return generate_pie_chart(filtered_transactions)
        if chart_type == 'pie_income':
            filtered_transactions = get_transactions_by_type(filtered_transactions, 'income')
            return generate_pie_chart(filtered_transactions)

        return redirect(url_for('report.report'))

    return redirect(url_for('report.report'))
