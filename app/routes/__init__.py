from .home.home import home_bp
from .home.import_file import import_bp
from .home.transactions import transactions_bp
from .categories import categories_bp
from .budget import budget_bp
from .report import report_bp
from .settings import settings_bp

def create_blueprints():
    return [
        home_bp,
        import_bp,
        transactions_bp,
        categories_bp,
        budget_bp,
        report_bp,
        settings_bp,
    ]
