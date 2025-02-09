# Personal Budget Manager

## Overview

Personal Budget Manager is a Flask-based web application designed to help users manage their personal finances effectively. The application provides a comprehensive set of features for tracking income and expenses, generating reports, setting budgets and visualizing financial data.


## Key Features

### Income and Expense Management
- Add, update and delete income and expense transactions.
- Assign transactions to categories.

### Category Management
- Create custom categories tailored to your needs.

### Reports and Visualizations
- Generate detailed financial reports.
- Visualize data using charts (e.g., pie charts).
- Download report files for offline use.

### Budget Tracking
- Set budget limits for each category.
- Receive warning when approaching or exceeding budget limits.

### Filtering
- Filter transactions by date, amount or category.
- Easily locate specific transactions.

### Import/Export
- Import financial data from CSV files.
- Export transactions to CSV or PDF for backup or analysis.

### Multi-Currency Support
- Support for multiple currencies.
- Automatic currency conversion using the [ExchangeRate-API](https://www.exchangerate-api.com/).


## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- A virtual environment (optional but recommended)
- An API key from [ExchangeRate-API](https://www.exchangerate-api.com/) for currency conversion.

### Steps to Run the Application

1. **Clone the Repository**
   ```bash
   git clone https://github.com/eramadanova/Expense-Tracker
   cd personal-budget-manager
# Setup and Run the Application

## 1. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Create a `.env` File

- Create a file named `.env` in the root directory of the project.
- Add the following content to the `.env` file:

```bash
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

- Replace `your_api_key_here` with your actual API key from [ExchangeRate-API](https://www.exchangerate-api.com/).
- Replace `your_secret_key_here` with a random string (e.g., generated using a tool like [RandomKeygen](https://randomkeygen.com/)).

### Example `.env` file:

```bash
EXCHANGE_RATE_API_KEY=12345abcdef67890
SECRET_KEY=supersecretkey12345
```

## 4. Run the Application

```bash
python app.py
```

## 5. Access the Application

Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Notes on `.env` File

- The `.env` file is used to store sensitive information like API keys and secret keys securely.
- Ensure that the `.env` file is added to your `.gitignore` file to prevent it from being committed to version control.

### Example `.gitignore` entry:

```bash
.env
