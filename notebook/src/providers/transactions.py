import logging

from eth_account.signers.local import LocalAccount

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError, TimeExhausted
from web3.module import Module
from web3.types import TxParams, Wei


logger = logging.getLogger(__name__)


class TransactionUtils(Module):
    w3: Web3

    @staticmethod
    def check(transaction: ContractFunction) -> bool:
        try:
            transaction.call()
        except (ValueError, ContractLogicError) as error:
            logger.error({'msg': 'Local transaction reverted.', 'error': str(error)})
            return False

        logger.info({'msg': 'Tx local call succeed.'})
        return True

    def send(
        self,
        transaction: ContractFunction,
        account: LocalAccount,
    ):
        pending = self.w3.eth.get_block('pending')

        gas_limit = self._estimate_gas(transaction, account.address)

        priority = 10 ** 9  # 1 gwei

        transaction_dict = transaction.build_transaction(
            TxParams(
                {
                    'from': account.address,
                    'gas': gas_limit,
                    'maxFeePerGas': Wei(pending['baseFeePerGas'] * 2 + priority),
                    'maxPriorityFeePerGas': priority,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                }
            )
        )

        signed = self.w3.eth.account.sign_transaction(transaction_dict, account._private_key)

        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        except Exception as error:
            logger.error({'msg': 'Transaction reverted.', 'value': str(error)})
            return

        logger.info({'msg': 'Transaction sent.', 'value': tx_hash.hex()})

        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, 100)
        except TimeExhausted:
            logger.info({'msg': 'Transaction timeout..', 'value': tx_hash.hex()})
        else:
            logger.info({'msg': 'Sent transaction included in blockchain.', 'value': tx_receipt['transactionHash'].hex()})

    @staticmethod
    def _estimate_gas(transaction: ContractFunction, account_address: ChecksumAddress) -> int:
        try:
            gas = transaction.estimate_gas({'from': account_address})
        except Exception as error:
            logger.warning({'msg': 'Can not estimate gas. Execution reverted.', 'error': str(error)})
            return 1000000

        return int(gas * 1.3)
