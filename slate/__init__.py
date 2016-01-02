"""Configures and starts the web server.
"""


from flask import Flask, render_template

from slate.endpoints.addapi import add_api
from slate.endpoints.indexpage import index_page
from slate.endpoints.viewpage import view_page


app = Flask(__name__, static_url_path='/static', static_folder='static')

# Server endpoints
app.register_blueprint(add_api)
app.register_blueprint(index_page)
app.register_blueprint(view_page)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

