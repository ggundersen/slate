"""Views expenses.
"""

import datetime
import json

from flask import Blueprint, render_template, request
from flask.ext.login import login_required

from slate import db
from slate.config import config


expenses = Blueprint('expenses',
                     __name__,
                     url_prefix='%s/expenses' % config.get('url', 'base'))


@expenses.route('', methods=['GET'])
@login_required
def expenses_default():
    """Renders expenses for current month.
    """
    category = request.args.get('category')
    year = request.args.get('year')
    month = request.args.get('month')
    categories = db.get_categories()
    sum_, expenses = db.get_expenses(category, year, month)
    return render_template('expenses.html',
                           categories=categories,
                           category_sum=sum_,
                           expenses=expenses)


@expenses.route('/all', methods=['GET'])
@login_required
def previous_expenses_list():
    """Renders a list of all expenses by month.
    """
    months_all = db.get_previous_months()
    return render_template('expenses-all.html',
                           months_all=months_all)


@expenses.route('/plot', methods=['GET'])
@login_required
def plot_previous_expenses():
    """Plots a time series of all previous expenses.
    """
    expenses_all = db.get_all_expenses_by_category()
    expenses_all = json.dumps(expenses_all, default=_date_handler)
    return render_template('expenses-plot.html',
                           data=expenses_all)


def _date_handler(date):
    """
    """
    return [date.year, date.month, date.day]

