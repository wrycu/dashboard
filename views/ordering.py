import datetime
import arrow
from flask import Blueprint, render_template, request
from db.model import Restaurant, Order, OrderItem, OrderMap

ordering = Blueprint('ordering', __name__, url_prefix='/ordering')


@ordering.route('/')
def landing():
    # data shows previous orders and their ratings
    data = []
    results = Restaurant.select()
    for result in results:
        orders = []
        raw_orders = Order.select().where(Order.restaurant_id == result.id).order_by(Order.order_date.desc())
        for raw_order in raw_orders:
            raw_order_items = OrderItem.select().join(OrderMap).where(OrderMap.order_id == raw_order.id)
            orders.append({
                'date': raw_order.order_date,
                'notes': raw_order.notes,
                'meals': [{
                    'id': raw_order_item.id,
                    'name': raw_order_item.name,
                    'min_price': raw_order_item.min_price,
                    'max_price': raw_order_item.max_price,
                    'last_price': raw_order_item.last_price,
                    'rating': raw_order_item.rating,
                    'notes': raw_order_item.notes,
                } for raw_order_item in raw_order_items],
            })
        data.append({
            'name': result.name,
            'rating': result.rating,
            'orders': orders,
        })

    # order_items shows items that have not been rated
    order_items = OrderItem.select(
        OrderItem,
        Restaurant.name.alias('restaurant_name'),
    ).where(
        OrderItem.rating.is_null()
    ).join(Restaurant).dicts()

    # suggestions shows suggestions for items to order based on past ratings
    suggestions = OrderItem.select(
        OrderItem,
        Restaurant.name.alias('restaurant_name'),
    ).where(
        OrderItem.last_order < arrow.get(datetime.datetime.now()).shift(days=-7).date()
    ).where(
        OrderItem.rating >= 3
    ).order_by(
        OrderItem.rating.desc(),
    ).join(
        Restaurant
    ).dicts()

    return render_template(
        'ordering/base.html',
        restaurants=data,
        order_items=order_items,
        suggestions=suggestions,
    )


@ordering.route('/rate', methods=['POST', 'DELETE'])
@ordering.route('/rate/<int:order_item_id>', methods=['POST', 'DELETE'])
def rate(order_item_id=None):
    """
    Rate (or delete the rating for) an order item
    :param order_item_id: ID of the order item to rate
    :return:
    """
    if request.method == 'POST':
        # rating or re-rating an item
        if request.form['rating']:
            rating = int(request.form['rating'])
            if rating < 1 or rating > 5:
                return 'Invalid rating', 400
            order_item = OrderItem.get(OrderItem.id == order_item_id)
            if not order_item:
                return 'Order item not found', 404
            order_item.rating = rating
            order_item.save()
            return 'OK'
    return 'OK'
