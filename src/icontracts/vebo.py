import json

from eth_account import Account
from eth_account.signers.local import LocalAccount

from utils.icontract import IContract


class IVEBO:
    def __init__(self, contract: IContract):
        self.contract = contract
        self.functions = contract.functions