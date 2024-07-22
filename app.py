from flask import Flask
import json
from db.model import database, create_tables

from views.vuln_mgmt import vuln_mgmt
from views.weight import weight
from views.ordering import ordering
from views.portal import portal


app = Flask(__name__)
app.config.from_file('config.json', load=json.load)

with app.app_context():
    # add the DB to the config
    app.config.update({'DB': {}})
    app.config['DB']['DB'] = database
    create_tables()

app.register_blueprint(vuln_mgmt)
app.register_blueprint(weight)
app.register_blueprint(ordering)
app.register_blueprint(portal)


@app.before_request
def before_request():
    # connect to the DB as we process a request
    app.config['DB']['DB'].connect()


@app.after_request
def after_request(response):
    # disconnect from the DB after we process a request
    app.config['DB']['DB'].close()
    return response


if __name__ == "__main__":
    app.run(debug=True, port=9191)
