import csv
import io
import matplotlib
matplotlib.use('Agg')  # Трябва да се извика преди да се импортира `pyplot`
import matplotlib.pyplot as plt
from flask import render_template, Blueprint, request, redirect, url_for, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils import get_categories, get_transactions
import config

report_bp = Blueprint('report', __name__)

def filter_by_category(filter_type, arguments: dict):
    transactions = get_transactions()
    filtered_transactions = []

    if filter_type == 'date':
        from_date = arguments.get('from_date')
        to_date = arguments.get('to_date')
        if from_date is not None and to_date is not None:
            filtered_transactions = [transaction for transaction in transactions if from_date <= transaction.date <= to_date]

    elif filter_type == 'amount':
        filter_amount = arguments.get('filter_amount')
        if filter_amount is not None:
            try:
                filter_amount = float(filter_amount)
                filtered_transactions = [ transaction for transaction in transactions if float(f"{transaction.amount:.2f}") == filter_amount]
            except ValueError:
                pass  # Ако не може да се конвертира в число, игнорираме

    elif filter_type == 'category':
        filter_category = arguments.get('filter_category')
        if filter_category is not None:
            try:
                filter_category = int(filter_category)
                filtered_transactions = [transaction for transaction in transactions if transaction.category_id == filter_category]
            except ValueError:
                pass  # Ако не може да се конвертира в число, игнорираме

    return filtered_transactions

@report_bp.route('/report', methods=['GET'])
def report():
    categories = get_categories()

    filter_type = request.args.get('filter_type')
    filtered_transactions = filter_by_category(filter_type, request.args)


    return render_template('report.html', categories=categories, filtered_transactions=filtered_transactions, default_currency=config.default_currency)

def generate_csv(transactions):
    output = io.StringIO()  # Временен текстов буфер
    writer = csv.writer(output)  # CSV writer, записва в `output`

    # Заглавен ред
    writer.writerow(['date', 'category', 'description', 'amount', 'currency'])

    # Записваме всяка транзакция
    for transaction in transactions:
        writer.writerow([transaction.date, transaction.category.name, transaction.description, f"{transaction.amount:.2f}", config.default_currency])

    # Създаваме HTTP отговор със съдържанието на `output`
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers['Content-Disposition'] = 'attachment; filename=report.csv'

    return response

def generate_pdf(transactions):
    output = io.BytesIO()  # Временен файл в паметта
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle('Transaction Report')

    # Начално позициониране на текста
    y_position = 750
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(230, y_position, 'Transaction Report')
    y_position -= 30

    # Заглавия на колоните
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_position, 'Date')
    pdf.drawString(130, y_position, 'Category')
    pdf.drawString(250, y_position, 'Description')
    pdf.drawString(400, y_position, 'Amount')
    pdf.drawString(500, y_position, 'Currency')
    y_position -= 20

    # Добавяне на данните от транзакциите
    pdf.setFont("Helvetica", 10)
    for transaction in transactions:
        if y_position < 50:  # Ако стигнем края на страницата, създаваме нова
            pdf.showPage()
            y_position = 750

        pdf.drawString(50, y_position, str(transaction.date))
        pdf.drawString(130, y_position, transaction.category.name)
        pdf.drawString(250, y_position, transaction.description)
        pdf.drawString(400, y_position, f"{transaction.amount:.2f}")
        pdf.drawString(500, y_position, config.default_currency)
        y_position -= 20

    pdf.save()
    output.seek(0)  # Връщаме се в началото на файла

    # Връщаме PDF файла като отговор
    response = Response(output.getvalue(), mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response

def generate_pie_chart(filtered_transactions):
    category_totals = dict()

    for transaction in filtered_transactions:
        category_name = transaction.category.name
        if category_name in category_totals:
            category_totals[category_name] += transaction.amount
        else:
            category_totals[category_name] = transaction.amount

    labels = category_totals.keys()
    sizes = category_totals.values()
    colors = plt.cm.Paired(range(len(labels)))

    plt.clf()  # Изчиства предишните графики
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')

    output = io.BytesIO()
    plt.savefig(output, format='png')
    plt.close()  # Затваря текущата фигура и освобождава паметта
    output.seek(0)

    response = Response(output.getvalue(), content_type='image/png')
    response.headers['Content-Disposition'] = 'attachment; filename=pie_chart.png'

    return response

@report_bp.route('/report-table', methods=['POST'])
def report_table():
    if request.method == 'POST':
        filtered_transaction_ids_str = request.form.get('filtered_transaction_ids')
        if filtered_transaction_ids_str is not None:
            try:
                filtered_transaction_ids = [int(id) for id in filtered_transaction_ids_str.split(',')]
            except ValueError:
                # Ако има проблем при преобразуването, игнорираме
                filtered_transaction_ids = []
        else:
            filtered_transaction_ids = []

        transactions = get_transactions()
        filtered_transactions = [transaction for transaction in transactions if transaction.id in filtered_transaction_ids]
        export_type = request.form['export_type']

        if export_type == 'pdf':
            return generate_pdf(filtered_transactions)
        elif export_type == 'csv':
            return generate_csv(filtered_transactions)

        return redirect(url_for('report.report'))

    return redirect(url_for('report.report'))

@report_bp.route('/report-chart', methods=['POST'])
def report_chart():
    if request.method == 'POST':
        filtered_transaction_ids_str = request.form.get('filtered_transaction_ids')
        if filtered_transaction_ids_str is not None:
            try:
                filtered_transaction_ids = [int(id) for id in filtered_transaction_ids_str.split(',')]
            except ValueError:
                # Ако има проблем при преобразуването, игнорираме
                filtered_transaction_ids = []
        else:
            filtered_transaction_ids = []

        transactions = get_transactions()
        filtered_transactions = [transaction for transaction in transactions if transaction.id in filtered_transaction_ids]

        chart_type = request.form['chart_type']
        print(chart_type)
        if chart_type == 'pie_expense':
            filtered_transactions = [transaction for transaction in filtered_transactions if transaction.category.category_type == 'expense']
            return generate_pie_chart(filtered_transactions)
        elif chart_type == 'pie_income':
            filtered_transactions = [transaction for transaction in filtered_transactions if transaction.category.category_type == 'income']
            print(filtered_transactions)
            return generate_pie_chart(filtered_transactions)

        return redirect(url_for('report.report'))

    return redirect(url_for('report.report'))


