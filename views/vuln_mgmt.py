from flask import Blueprint, render_template, Response, request
import json
from db.model import Nessus

vuln_mgmt = Blueprint('vuln_mgmt', __name__, url_prefix='/vuln')


@vuln_mgmt.route('/')
def landing():
    alerts = Nessus.select()
    print(alerts)
    return render_template('vuln_mgmt/base.html', alerts=alerts)


@vuln_mgmt.route('/alerts', methods=['GET', 'POST'])
@vuln_mgmt.route('/alerts/<int:alert>', methods=['GET', 'POST', 'DELETE'])
def records(alert=None):
    if request.method == 'POST':
        submitted_name = request.form['name']
        submitted_action = request.form['action']
        submitted_identifier = request.form['identifier']
        submitted_rationale = request.form['rationale']
        if not submitted_name or not submitted_action or not submitted_identifier or not submitted_rationale:
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Missing required data',
                }),
                400,
            )
        temp = Nessus.create(
            name=submitted_name,
            action=submitted_action,
            identifier=submitted_identifier,
            rationale=submitted_rationale,
        )
        temp.save()
        return Response(
            json.dumps({
                'success': True,
            }),
            200,
        )
    elif request.method == 'GET':
        if alert:
            retrieved_record = Nessus.get(Nessus.id == alert)
            return Response(
                json.dumps({
                    'weight': retrieved_record.weight,
                    'date': retrieved_record.date,
                }),
                200,
            )
    elif request.method == 'DELETE':
        if alert:
            retrieved_record = Nessus.get(Nessus.id == alert)
            retrieved_record.delete_instance()
            return Response(
                json.dumps({
                    'success': True,
                }),
                200,
            )
    return Response('Unknown state', 400)
