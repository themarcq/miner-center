import requests
import logging
from .exceptions import NanopoolError
import time


logger = logging.getLogger('nanopool')


class NanopoolConnector:
    PROTOCOL = 'https'
    BASE_URL = "api.nanopool.org/v1/eth"
    GENERAL_INFO_ENDPOINT = 'user'
    PAYMENTS_INFO_ENDPOINT = 'payments'

    def __init__(self, address):
        super(NanopoolConnector, self).__init__()
        self.address = address

    def fetch_endpoint_data(self, endpoint):
        try:
            req = requests.get(
                "{protocol}://{base_url}/{endpoint}/{address}".format(
                    protocol = self.PROTOCOL,
                    base_url=self.BASE_URL,
                    endpoint=endpoint,
                    address=self.address
                )
            )
            if req.status_code // 100 != 2:
                req.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return {'error': e}

        return req.json()

    def fetch_last_payment_date(self):
        data = self.fetch_endpoint_data(self.PAYMENTS_INFO_ENDPOINT)
        if data['status']:
            if len(data['data']) > 0:
                return {
                    'last_payment_date': data['data'][0]['date']
                }
            return {'last_payment_date': 0}
        return {'error': data['error']}

    def fetch_general_info(self):
        data = self.fetch_endpoint_data(self.GENERAL_INFO_ENDPOINT)
        if data['status']:
            data = data['data']
            return {
                'balance': data['balance'],
                'balance_percent': float(data['balance'])*500,
                'hashrate': data['hashrate'],
                'avgHashrate': data['avgHashrate']
            }
        return {'error': data['error']}

    def get_data(self):
        general_info = self.fetch_general_info()
        last_payment_date = self.fetch_last_payment_date()
        if last_payment_date.get('last_payment_date', None) is not None:
             avg_eth = float(general_info.get('balance', 0)) / ((time.time() - last_payment_date['last_payment_date']) / (60*60*24))
             # trimming float precision
             avg_eth = float(int(avg_eth * 100000000))/100000000
             general_info['daily_ethereum'] = avg_eth
        return general_info
