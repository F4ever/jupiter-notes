from eth_typing import ChecksumAddress
from web3 import Web3 as _Web3, HTTPProvider
from web3.beacon import Beacon
from web3.module import Module

from providers.etherscan import Etherscan
from providers.transactions import TransactionUtils
from utils.extend_by_key import extend
from utils.icontract import IContract
from variables import M_EL_URL, M_CL_URL, ETHERSCAN_API_KEY, H_CL_URL, H_EL_URL


class ContractLoader(Module):
    w3: 'Web3'

    def load(self,  address: ChecksumAddress, abi: list | None = None) -> IContract:
        if abi is None:
            abi = self.w3.etherscan.get_contract_abi(address)

        contract = self.w3.eth.contract(address, abi=abi)
        print('Load abi')

        impl_address = None
        functions = [f.abi['name'] for f in contract.all_functions()]
        if 'proxy__getImplementation' in functions:
            impl_address = contract.functions.proxy__getImplementation().call()
        elif 'implementation' in functions:
            impl_address = contract.functions.implementation().call()

        if impl_address:
            impl_abi = self.w3.etherscan.get_contract_abi(impl_address)
            abi = extend(abi, impl_abi, 'name')
            print('Load implementation')

        contract: IContract = self.w3.eth.contract(
            address,
            abi=abi,
            ContractFactoryClass=IContract,
            decode_tuples=True,
        )
        contract.spoiler()
        return contract


class Web3(_Web3):
    cl: Beacon
    etherscan: Etherscan
    contract: ContractLoader

    def mainnet(self):
        self.provider = HTTPProvider(M_EL_URL)

        del self.cl
        del self.etherscan

        self.attach_modules({
            'cl': lambda: Beacon(M_CL_URL),
            'etherscan': lambda: Etherscan(ETHERSCAN_API_KEY, w3.eth.chain_id),
        })

    def holesky(self):
        self.provider = HTTPProvider(H_EL_URL)

        del self.cl
        del self.etherscan

        self.attach_modules({
            'cl': lambda: Beacon(H_CL_URL),
            'etherscan': lambda: Etherscan(ETHERSCAN_API_KEY, w3.eth.chain_id),
        })


w3 = Web3(HTTPProvider(M_EL_URL))


w3.attach_modules({
    'cl': lambda: Beacon(M_CL_URL),
    'etherscan': lambda: Etherscan(ETHERSCAN_API_KEY, w3.eth.chain_id),
    'contract': ContractLoader,
    'transaction': TransactionUtils,
})
