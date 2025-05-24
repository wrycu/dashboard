import datetime
import arrow
from flask import Blueprint, render_template, request
from db.model import Restaurant, Order, OrderItem, OrderMap

portal = Blueprint('portal', __name__, url_prefix='/')


@portal.route('/')
def landing():
    sites = [
        {
            'name': 'Mealie',
            'fav_ico': 'https://mealie.wrycu.com/favicon.ico',
            'description': 'Recipe book, meal prep helper',
            'url': 'https://mealie.wrycu.com/',
        },
        {
            'name': 'Paperless-NGX',
            'fav_ico': 'https://documents.wrycu.com/favicon.ico',
            'description': 'Document management system',
            'url': 'https://documents.wrycu.com/',
        },
        {
            'name': 'Pi-hole',
            'fav_ico': 'https://dns.wrycu.com/admin/img/favicons/favicon.ico',
            'description': 'DNS, DNS black hole, ad blockingr',
            'url': 'https://dns.wrycu.com/admin/',
        },
        {
            'name': 'FoundryVTT',
            'fav_ico': 'https://swrpg.wrycu.com/icons/vtt-512.png',
            'description': 'TTRPG platform',
            'url': 'https://swrpg.wrycu.com',
        },
        {
            'name': 'Monica',
            'fav_ico': 'https://monica.wrycu.com/img/monica.svg',
            'description': 'Relationship management software',
            'url': 'https://monica.wrycu.com/',
        },
        {
            'name': 'Immich',
            'fav_ico': 'https://photos.wrycu.com/favicon.ico',
            'description': 'Photo management software',
            'url': 'https://photos.wrycu.com/',
        },
        {
            'name': 'Kerner',
            'fav_ico': 'https://kener.ing/logo96.png',
            'description': 'Uptime and status alerting',
            'url': 'https://status.wrycu.com/',
        },
        {
            'name': 'Actual Budget',
            'fav_ico': 'https://budget.wrycu.com/favicon.ico',
            'description': 'Budgeting software',
            'url': 'https://budget.wrycu.com',
        },
        {
            'name': 'Yamtrack',
            'fav_ico': 'https://track.wrycu.com/static/favicon/favicon.ico',
            'description': 'Track movie and TV show watching',
            'url': 'https://track.wrycu.com',
        },
        {
            'name': 'Jellyfin',
            'fav_ico': 'https://media.wrycu.com/web/touchicon144.png',
            'description': 'Watch my media',
            'url': 'https://media.wrycu.com',
        },
    ]
    return render_template('portal/base.html', sites=sites)
