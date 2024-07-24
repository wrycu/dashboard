import httpx
import json
import arrow
from db import model


class FoodParser:
    def __init__(self):
        self.cookies = {}
        self.load_cookies()
        self.base_url = json.load(open('config.json'))['FOOD']['BASE_URL']
        self.client = httpx.Client(http2=True)
        self.headers = {
            'Content-Type': 'application/json',
            'Referrer': 'https://www.doordash.com/orders/',
            'Origin': 'https://www.doordash.com',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Apollographql-Client-Name': '@doordash/app-consumer-production-ssr-client',
            'Apollographql-Client-Version': '3.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        self.order_query = {"operationName": "getConsumerOrdersWithDetails",
         "variables": {"offset": 0, "limit": 10, "includeCancelled": False},
         "query": "query getConsumerOrdersWithDetails($offset: Int!, $limit: Int!, $includeCancelled: Boolean) {\n  getConsumerOrdersWithDetails(\n    offset: $offset\n    limit: $limit\n    includeCancelled: $includeCancelled\n  ) {\n    id\n    orderUuid\n    deliveryUuid\n    createdAt\n    submittedAt\n    cancelledAt\n    fulfilledAt\n    specialInstructions\n    isConsumerSubscriptionEligible\n    isGroup\n    isReorderable\n    isGift\n    isPickup\n    isMerchantShipping\n    containsAlcohol\n    fulfillmentType\n    shoppingProtocol\n    creator {\n      ...ConsumerOrderCreatorFragment\n      __typename\n    }\n    deliveryAddress {\n      id\n      formattedAddress\n      __typename\n    }\n    orders {\n      id\n      creator {\n        ...ConsumerOrderCreatorFragment\n        __typename\n      }\n      items {\n        ...ConsumerOrderOrderItemFragment\n        __typename\n      }\n      __typename\n    }\n    paymentCard {\n      ...ConsumerOrderPaymentCardFragment\n      __typename\n    }\n    grandTotal {\n      unitAmount\n      currency\n      decimalPlaces\n      displayString\n      sign\n      __typename\n    }\n    likelyOosItems {\n      menuItemId\n      name\n      photoUrl\n      __typename\n    }\n    pollingInterval\n    store {\n      id\n      name\n      business {\n        id\n        name\n        __typename\n      }\n      phoneNumber\n      fulfillsOwnDeliveries\n      customerArrivedPickupInstructions\n      isPriceMatchingEnabled\n      priceMatchGuaranteeInfo {\n        headerDisplayString\n        bodyDisplayString\n        buttonDisplayString\n        __typename\n      }\n      __typename\n    }\n    recurringOrderDetails {\n      itemNames\n      consumerId\n      recurringOrderUpcomingOrderUuid\n      scheduledDeliveryDate\n      arrivalTimeDisplayString\n      storeName\n      isCancelled\n      __typename\n    }\n    bundleOrderInfo {\n      ...BundleOrderInfoFragment\n      __typename\n    }\n    cancellationPendingRefundInfo {\n      state\n      originalPaymentAmount {\n        unitAmount\n        currency\n        decimalPlaces\n        displayString\n        sign\n        __typename\n      }\n      creditAmount {\n        unitAmount\n        currency\n        decimalPlaces\n        displayString\n        sign\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ConsumerOrderPaymentCardFragment on ConsumerOrderPaymentCard {\n  id\n  last4\n  type\n  __typename\n}\n\nfragment ConsumerOrderOrderItemFragment on ConsumerOrderOrderItem {\n  id\n  name\n  quantity\n  specialInstructions\n  substitutionPreferences\n  orderItemExtras {\n    ...ConsumerOrderOrderItemExtraFragment\n    __typename\n  }\n  purchaseQuantity {\n    ...ConsumerOrderQuantityFragment\n    __typename\n  }\n  fulfillQuantity {\n    ...ConsumerOrderQuantityFragment\n    __typename\n  }\n  originalItemPrice\n  purchaseType\n  __typename\n}\n\nfragment ConsumerOrderOrderItemExtraOptionFields on OrderItemExtraOption {\n  menuExtraOptionId\n  name\n  description\n  price\n  quantity\n  __typename\n}\n\nfragment ConsumerOrderOrderItemExtraOptionFragment on OrderItemExtraOption {\n  ...ConsumerOrderOrderItemExtraOptionFields\n  orderItemExtras {\n    ...ConsumerOrderOrderItemExtraFields\n    orderItemExtraOptions {\n      ...ConsumerOrderOrderItemExtraOptionFields\n      orderItemExtras {\n        ...ConsumerOrderOrderItemExtraFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ConsumerOrderOrderItemExtraFields on OrderItemExtra {\n  menuItemExtraId\n  name\n  __typename\n}\n\nfragment ConsumerOrderOrderItemExtraFragment on OrderItemExtra {\n  ...ConsumerOrderOrderItemExtraFields\n  orderItemExtraOptions {\n    ...ConsumerOrderOrderItemExtraOptionFragment\n    __typename\n  }\n  __typename\n}\n\nfragment ConsumerOrderCreatorFragment on ConsumerOrderCreator {\n  id\n  firstName\n  lastName\n  __typename\n}\n\nfragment ConsumerOrderQuantityFragment on Quantity {\n  continuousQuantity {\n    quantity\n    unit\n    __typename\n  }\n  discreteQuantity {\n    quantity\n    unit\n    __typename\n  }\n  __typename\n}\n\nfragment BundleOrderInfoFragment on BundleOrderInfo {\n  primaryBundleOrderUuid\n  primaryBundleOrderId\n  bundleOrderUuids\n  bundleOrderConfig {\n    ...BundleOrderConfigFragment\n    __typename\n  }\n  __typename\n}\n\nfragment BundleOrderConfigFragment on BundleOrderConfig {\n  bundleType\n  bundleOrderRole\n  __typename\n}\n"}

    def load_cookies(self):
        """
            Load the cookies from the config file
            :return:
            """
        config = json.load(open('config.json'))
        cookies = {}
        for cookie_name, cookie_value in config['FOOD']['AUTH'].items():
            cookies[cookie_name] = cookie_value
        self.cookies = cookies

    def get_and_insert_orders(self, offset=0, limit=10):
        reply = self.client.post(
            f'{self.base_url}/getConsumerOrdersWithDetails?operation=getConsumerOrdersWithDetails',
            headers=self.headers,
            cookies=self.cookies,
            data=json.dumps(self.order_query),
        )

        api_reply = json.loads(reply.content)

        for entry in api_reply['data']['getConsumerOrdersWithDetails']:
            for order in entry['orders']:
                order_date = arrow.get(entry['submittedAt']).date()
                inserted_restaurant = model.Restaurant.get_or_create(
                    name=entry['store']['name'],
                    defaults={'last_order': order_date},
                )[0]

                inserted_order = model.Order.get_or_create(
                    restaurant_id=inserted_restaurant.id,
                    order_date=order_date,
                )[0]

                for item in order['items']:
                    item_name = item['name']
                    try:
                        item_price = int(str(item['originalItemPrice'])[:-2])
                    except ValueError:
                        # the price is sometimes not present in this field.
                        # give up as this is a nice-to-have value anyway
                        item_price = -1

                    inserted_item = model.OrderItem.get_or_create(
                        restaurant_id=inserted_restaurant.id,
                        name=item_name,
                        defaults={
                            'min_price': item_price,
                            'max_price': item_price,
                            'last_price': item_price,
                            'last_order': order_date,
                        }
                    )[0]

                    if order_date > inserted_item.last_order:
                        inserted_item.last_order = order_date
                    if item_price < inserted_item.min_price:
                        inserted_item.min_price = item_price
                    if item_price > inserted_item.max_price:
                        inserted_item.max_price = item_price
                    inserted_item.save()

                    model.OrderMap.create(
                        item_id=inserted_item.id,
                        order_id=inserted_order.id,
                    )


class NessusAlerter:
    def __init__(self):
        config = json.load(open('config.json'))
        self.base_url = config['NESSUS']['BASE_URL']
        self.secret_key = config['NESSUS']['SECRET_KEY']
        self.access_key = config['NESSUS']['ACCESS_KEY']
        self.rules = self.load_rules()
        self.alerts = []
        self.slack = {
            'WEBHOOK_URL': config['SLACK']['WEBHOOK_URL'],
            'ACCESS_TOKEN': config['SLACK']['ACCESS_TOKEN'],
        }

    @staticmethod
    def load_rules():
        data = {
            'alert': {
                'cve': [],
                'cvss': [],
                'pluginid': [],
            },
            'ignore': {
                'cve': [],
                'cvss': [],
                'pluginid': [],
            },
        }
        for alert in model.Nessus.select().where(model.Nessus.action == 'ALERT'):
            if alert.identifier.startswith('cve:'):
                data['alert']['cve'].append(alert.identifier.replace('cve:', ''))
            elif alert.identifier.startswith('cvss:'):
                data['alert']['cvss'].append(int(alert.identifier.replace('cvss:', '')))
            elif alert.identifier.startswith('pluginid:'):
                data['alert']['pluginid'].append(alert.identifier.replace('pluginid:', ''))
        for alert in model.Nessus.select().where(model.Nessus.action == 'IGNORE'):
            if alert.identifier.startswith('cve:'):
                data['ignore']['cve'].append(alert.identifier.replace('cve:', ''))
            elif alert.identifier.startswith('cvss:'):
                data['ignore']['cvss'].append(int(alert.identifier.replace('cvss:', '')))
            elif alert.identifier.startswith('pluginid:'):
                data['ignore']['pluginid'].append(alert.identifier.replace('pluginid:', ''))
        return data

    def make_request(self, method, endpoint='/', data=None):
        if method == 'GET':
            reply = httpx.get(
                f'{self.base_url}{endpoint}',
                headers={
                    'X-ApiKeys': f'accessKey={self.access_key}; secretKey={self.secret_key}',
                },
                verify=False,
            )
        elif method == 'POST':
            reply = httpx.post(
                f'{self.base_url}{endpoint}',
                headers={
                    'X-ApiKeys': f'accessKey={self.access_key}; secretKey={self.secret_key}',
                },
                data=data,
                verify=False,
            )
        else:
            raise ValueError(f'Unsupported method {method}')
        reply.raise_for_status()
        return reply

    def scan_and_alert(self):
        scan_id = 29  # LAN scan
        scan_details = self.get_scan_details(scan_id)
        for plugin in scan_details['prioritization']['plugins']:
            should_alert, details = self.should_alert(plugin)
            report_link = f'{self.base_url}/#/scans/reports/{scan_id}/vulnerabilities/group/{plugin["pluginid"]}/{plugin["pluginid"]}'
            if should_alert:
                self.slack_notify(f'{details} - {report_link}')

    def get_scan_details(self, scan_id):
        return self.make_request('GET', f'/scans/{scan_id}').json()

    def get_plugin_details(self, plugin_id):
        return self.make_request('GET', f'/plugins/plugin/{plugin_id}').json()

    def should_alert(self, plugin):
        plugin_id = plugin['pluginid']
        plugin_details = self.get_plugin_details(plugin_id)['attributes']
        plugin_cves = [x['attribute_value'] for x in plugin_details if x['attribute_name'] == 'cve']

        hosts = ', '.join([x['host_ip'] for x in plugin['hosts']])
        plugin_name = plugin['pluginname']
        known_exploit = [x['attribute_value'] for x in plugin_details if x['attribute_name'] == 'exploit_available']
        plugin_score = plugin['severity']

        # check if the plugin is explicitly ignored
        if plugin_id in self.rules['ignore']['pluginid']:
            return False, f"Plugin {plugin_id} explicitly ignored"
        # check if the plugin is explicitly alerted
        if plugin_id in self.rules['alert']['pluginid']:
            return True, f'Found {plugin_name} on {hosts} (alerted due to plugin)'
        # check if plugin has an alert score
        if [x for x in self.rules['alert']['cvss'] if plugin_score >= x]:
            return True, f'Found {plugin_name} on {hosts} (alerted due to severity)'
        # check if plugin CVEs exist in our alert CVE list
        if [x for x in plugin_cves if x in self.rules['alert']['cve']]:
            return True, f'Found {plugin_name} on {hosts} (alerted due to CVE)'

        return False, None

    def slack_notify(self, message):
        reply = httpx.post(
            self.slack['WEBHOOK_URL'],
            headers={'Content-Type': 'application/json'},
            json={
                'text': message,
            },
        )
        reply.raise_for_status()


nessus_scanner = NessusAlerter()
nessus_scanner.scan_and_alert()

food_parser = FoodParser()
food_parser.get_and_insert_orders()
