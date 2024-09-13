import json
from functools import lru_cache

import requests
from eth_typing import ChecksumAddress
from requests import Response


class Etherscan:
    API = {
        1: 'https://api.etherscan.io/api',
        17000: 'https://api-holesky.etherscan.io/api',
    }

    def __init__(self, api_key: str, chain_id: int):
        self.key = api_key
        self.url = self.API[chain_id]

    def _get(self, params: dict):
        params['apikey'] = self.key

        return json.loads(requests.get(
            self.url,
            params=params,
        ).json()['result'])

    @lru_cache(maxsize=20)
    def get_contract_abi(self, address: ChecksumAddress) -> Response:
        return self._get({
            'module': 'contract',
            'action': 'getabi',
            'address': address,
        })
