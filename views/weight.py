import json
import arrow
import datetime
from flask import Blueprint, render_template, request, Response
from db.model import Weight

weight = Blueprint('weight', __name__, url_prefix='/weight')


@weight.route('/')
def landing():
    """
    renders the base weight page, which includes a form to log weight and data for two charts
        the first chart shows all recorded weights
        the second shows the weekly average of recorded weights
    :return:
    """
    weights = Weight.select().order_by(Weight.date.asc())
    start_date = (arrow.now() - datetime.timedelta(weeks=3)).date()
    raw_rolling_averages = Weight.select().where(Weight.date >= start_date).order_by(Weight.date.asc())
    rolling_averages = {
        'avgs': [],
        'dates': [],
    }
    tmp_averages = {}
    for record in raw_rolling_averages:
        year, week = record.date.isocalendar()[0], record.date.isocalendar()[1]
        if year not in tmp_averages:
            tmp_averages[year] = {}
        if week not in tmp_averages[year]:
            tmp_averages[year][week] = {'total': 0, 'count': 0}
        tmp_averages[year][week]['total'] += record.weight
        tmp_averages[year][week]['count'] += 1

    for year, weeks in tmp_averages.items():
        for week, data in weeks.items():
            rolling_averages['avgs'].append(int(data['total'] / data['count']))
            rolling_averages['dates'].append(str(datetime.datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()))

    return render_template(
        'weight/base.html',
        records=weights,
        rolling_averages=rolling_averages,
    )


@weight.route('/records', methods=['GET', 'POST'])
@weight.route('/records/<int:record>', methods=['GET', 'POST', 'DELETE'])
def records(record=None):
    if request.method == 'POST':
        submitted_weight = request.form['weight']
        submitted_date = arrow.get(request.form['date']).date()
        if not submitted_weight or not submitted_date:
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Missing weight or date',
                }),
                400,
            )
        temp = Weight.create(weight=submitted_weight, date=submitted_date)
        temp.save()
        return Response(
            json.dumps({
                'success': True,
            }),
            200,
        )
    elif request.method == 'GET':
        if record:
            retrieved_record = Weight.get(Weight.id == record)
            return Response(
                json.dumps({
                    'weight': retrieved_record.weight,
                    'date': retrieved_record.date,
                }),
                200,
            )
    elif request.method == 'DELETE':
        if record:
            retrieved_record = Weight.get(Weight.id == record)
            retrieved_record.delete_instance()
            return Response(
                json.dumps({
                    'success': True,
                }),
                200,
            )
    return Response('Unknown state', 400)
