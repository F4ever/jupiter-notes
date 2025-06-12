import json

from eth_account import Account
from eth_account.signers.local import LocalAccount

from utils.icontract import IContract


class ICuratedModule:
    def __init__(self, contract: IContract):
        self.contract = contract
        self.functions = contract.functions

    @property
    def node_operators(self):
        ids = self.functions.getNodeOperatorIds(0, 10000).call()

        res = []
        for id in ids:
            no_data = self.functions.getNodeOperator(id, True).call()._asdict()
            no_additional_data = self.functions.getNodeOperatorSummary(id).call()._asdict()
            no_data.update(no_additional_data)
            res.append(no_data)

        return res

    def add_node_operator(self, no_name: str, account: LocalAccount):
        no_acc = Account.create()

        print(
            f"Adding {no_name}. Account address: {no_acc.address}. Account pk: {no_acc._private_key}."
        )

        operator = self.functions.addNodeOperator(no_name, no_acc.address)

        self.contract.w3.transaction.send(operator, account)

        with open('../secrets/nos', 'rw') as f:
            data = f.read()
            if not data:
                pks = []
            else:
                pks = json.loads(data)

            pks.append({
                'name': no_name,
                'address': no_acc.address,
                'pk': no_acc._private_key,
            })

            f.write(json.dumps(pks))

    def add_keys(self):
        pass
