"""
    Initializes and registers all route blueprints for the application.
"""
from .home.home import home_bp
from .home.import_file import import_bp
from .home.transactions import transactions_bp
from .categories import categories_bp
from .budget import budget_bp
from .report import report_bp
from .settings import settings_bp

def create_blueprints():
    """
    Creates and returns a list of Flask blueprints for different route modules.

    :return: List of registered blueprints.
    """

    return [
        home_bp,
        import_bp,
        transactions_bp,
        categories_bp,
        budget_bp,
        report_bp,
        settings_bp
    ]
