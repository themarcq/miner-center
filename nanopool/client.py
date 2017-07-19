import requests
import logging


logger = logging.getLogger('nanopool')


class NanopoolConnector:
    PROTOCOL = 'https'
    BASE_URL = "api.nanopool.org/v1/eth"
    GENERAL_INFO_ENDPOINT = 'user'

    def __init__(self, address):
        super(NanopoolConnector, self).__init__()
        self.address = address

    def fetch_general_info(self):
        try:
            req = requests.get(
                "{protocol}://{base_url}/{endpoint}/{address}".format(
                    protocol = self.PROTOCOL,
                    base_url=self.BASE_URL,
                    endpoint=self.GENERAL_INFO_ENDPOINT,
                    address=self.address
                )
            )
            if req.status_code // 100 != 2:
                req.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return {'error': e}

        data = req.json()
        if data['status']:
            data = data['data']
            return {
                'balance': data['balance'],
                'balance_percent': float(data['balance'])*500,
                'hashrate': data['hashrate'],
                'avgHashrate': data['avgHashrate']
            }
        return {'error': data['error']}
