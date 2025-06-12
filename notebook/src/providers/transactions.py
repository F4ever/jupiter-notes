import logging

from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError, TimeExhausted
from web3.module import Module
from web3.types import TxReceipt, Wei, TxParams, BlockData


logger = logging.getLogger(__name__)


def get_input():
    return input()


def prompt(prompt_message: str) -> bool:
    print(prompt_message, end='')
    while True:
        choice = get_input().lower()

        if choice in ['Y', 'y']:
            return True

        if choice in ['N', 'n']:
            return False

        print('Please respond with [y or n]: ', end='')


class TransactionUtils(Module):
    w3: Web3

    def check_and_send_transaction(self, transaction, account: LocalAccount | None = None, force=False) -> TxReceipt | None:
        if not account:
            logger.info({'msg': 'No account provided to submit extra data. Dry mode'})
            return None

        params = self._get_transaction_params(transaction, account)

        if self._check_transaction(transaction, params):

            if not force:
                self._manual_tx_processing(transaction, params, account)
            else:
                self._sign_and_send_transaction(transaction, params, account)

    def _manual_tx_processing(self, transaction, params: TxParams, account: LocalAccount):
        logger.warning({'msg': 'Send transaction in manual mode.'})
        msg = (
            '\n'
            'Going to send transaction to blockchain: \n'
            f'Tx args:\n{transaction.args}\n'
            f'Tx params:\n{params}\n'
        )
        if prompt(f'{msg}Should we send this TX? [y/n]: '):
            return self._sign_and_send_transaction(transaction, params, account)

    @staticmethod
    def _check_transaction(transaction, params: TxParams) -> bool:
        """
        Returns:
        True - transaction succeed.
        False - transaction reverted.
        """
        logger.info({"msg": "Check transaction. Make static call.", "value": transaction.args})

        try:
            result = transaction.call(params)
        except (ValueError, ContractLogicError) as error:
            logger.error({"msg": "Transaction reverted.", "error": str(error)})
            return False

        logger.info({"msg": "Transaction executed successfully.", "value": result})
        return True

    def _get_transaction_params(self, transaction: ContractFunction, account: LocalAccount):
        # get pending block doesn't work on erigon node in specific cases
        latest_block: BlockData = self.w3.eth.get_block("latest")

        params: TxParams = {
            "from": account.address,
            "maxFeePerGas": Wei(
                latest_block["baseFeePerGas"] * 2 + 10**9
            ),
            "maxPriorityFeePerGas": 10**9,
            "nonce": self.w3.eth.get_transaction_count(account.address),
        }

        if gas := self._estimate_gas(transaction, account):
            params['gas'] = gas

        return params

    @staticmethod
    def _estimate_gas(transaction: ContractFunction, account: LocalAccount) -> int | None:
        """If transaction throws exception return None"""
        try:
            gas = transaction.estimate_gas({'from': account.address})
        except ContractLogicError as error:
            logger.warning({'msg': 'Can not estimate gas. Contract logic error.', 'error': str(error)})
            return None
        except ValueError as error:
            logger.warning({'msg': 'Can not estimate gas. Execution reverted.', 'error': str(error)})
            return None

        return gas + 100000

    def _sign_and_send_transaction(
        self,
        transaction: ContractFunction,
        params: TxParams | None,
        account: LocalAccount,
    ) -> TxReceipt | None:
        tx = transaction.build_transaction(params)
        signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)

        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info({"msg": "Transaction sent.", "value": tx_hash.hex()})

        return self._handle_sent_transaction(tx_hash)

    def _handle_sent_transaction(self, transaction_hash: HexBytes) -> TxReceipt | None:
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        except TimeExhausted:
            logger.warning({"msg": "Transaction was not found in blockchain after 120 seconds."})
            return None

        logger.info(
            {
                "msg": "Transaction is in blockchain.",
                "blockHash": tx_receipt["blockHash"].hex(),
                "blockNumber": tx_receipt["blockNumber"],
                "gasUsed": tx_receipt["gasUsed"],
                "effectiveGasPrice": tx_receipt["effectiveGasPrice"],
                "status": tx_receipt["status"],
                "transactionHash": tx_receipt["transactionHash"].hex(),
                "transactionIndex": tx_receipt["transactionIndex"],
            }
        )

        return tx_receipt
