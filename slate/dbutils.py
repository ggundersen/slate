"""Utility functions for data that does not need a model.
"""

import calendar
from   datetime import datetime

from flask_login import current_user

from slate import db


def get_all_months():
    """Gets all previous months with recorded transactions.
    """
    conn = db.engine.connect()
    tuples = conn.execute(
        'SELECT '
        '  MONTH(`date_time`), '
        '  YEAR(`date_time`), '
        '  SUM(`cost`) '
        'FROM `expense` '
        'JOIN `user` '
        '  ON `user`.`id` = `expense`.`user_fk` '
        'WHERE `user`.name = "%s" '
        'GROUP BY '
        '  MONTH(`date_time`), '
        '  YEAR(`date_time`) '
        'ORDER BY MONTH(`date_time`) ASC' % current_user.name
    )
    results = [{
        'view': '%s %s' % (calendar.month_name[c[0]], c[1]),
        'month_num': c[0],
        'year_num': c[1],
        'total': c[2]} for c in tuples.fetchall()]
    conn.close()
    return sorted(results,
                  key=lambda obj: datetime.strptime(obj['view'], '%B %Y'))


def get_category_subtotals(year=None, month=None):
    """Returns total expenses per category, excluding rent.
    """
    results = []
    if not (year and month):
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        year = int(year)
        month = int(month)
    categories = [c for c in current_user.categories]
    for category in categories:
        expenses = [e.cost for e in category.expenses if
                    e.user.name == current_user.name and
                    e.date_time.year == year and
                    e.date_time.month == month]
        results.append({
            'category': category.name.capitalize(),
            'subtotal': round(sum(expenses), 2)
        })
    return results


def get_category_subtotals_for_year(year):
    """Returns total expenses per category.
    """
    results = []
    categories = [c for c in current_user.categories]
    for category in categories:
        expenses = [e.cost for e in category.expenses if
                    e.user.name == current_user.name and
                    e.date_time.year == year]
        results.append({
            'category': category.name.capitalize(),
            'subtotal': round(sum(expenses), 2)
        })
    return results


def get_repeated_expenses(year, min_num_repeated):
    """Returns expenses with repeated comments, lower bound of min_.
    """
    conn = db.engine.connect()
    tuples = conn.execute(
        'SELECT '\
        '  expense.comment, SUM(expense.cost) '\
        'FROM expense '\
        'JOIN user '\
        '  ON user.id = expense.user_fk '\
        'WHERE '\
        '  user.name = "%s" '\
        '  AND YEAR(expense.date_time) = %s '\
        'GROUP BY expense.comment '\
        'HAVING COUNT(expense.comment) >= %s' % (current_user.name, year, min_num_repeated)
    )
    results = {}
    for comment, cost in tuples.fetchall():
        if comment not in results:
            results[comment] = 0
        results[comment] += cost
    conn.close()
    return results
