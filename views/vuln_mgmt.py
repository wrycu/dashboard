from flask import Blueprint, render_template

vuln_mgmt = Blueprint('vuln_mgmt', __name__)


@vuln_mgmt.route('/')
def landing():
    return render_template('landing.html')
