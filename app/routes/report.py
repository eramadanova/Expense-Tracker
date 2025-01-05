from flask import render_template, Blueprint

report_bp = Blueprint('report', __name__)

@report_bp.route('/report')
def report():
    return render_template('report.html')
