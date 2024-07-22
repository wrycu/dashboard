import datetime
import arrow
from flask import Blueprint, render_template, request
from db.model import Restaurant, Order, OrderItem, OrderMap

portal = Blueprint('portal', __name__, url_prefix='/')


@portal.route('/')
def landing():
    return render_template('portal/base.html')
