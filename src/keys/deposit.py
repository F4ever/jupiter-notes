import sys
from typing import cast

from web3 import Web3, HTTPProvider

import variables
from blockchain.contracts.deposit import DepositContract
from blockchain.contracts.lido import LidoContract
from blockchain.contracts.staking_router import StakingRouterContractV2
from blockchain.web3_extentions.lido_contracts import LidoContracts
from blockchain.web3_extentions.transaction import TransactionUtils
from utils.bytes import from_hex_string_to_bytes
from py_ecc.bls import G2ProofOfPossession as bls

from ssz import (
    ByteVector,
    Serializable,
    uint64,
    bytes4,
    bytes32,
    bytes48,
    bytes96
)

DOMAIN_DEPOSIT = bytes.fromhex('03000000')
ZERO_BYTES32 = b'\x00' * 32

bytes8 = ByteVector(8)
bytes20 = ByteVector(20)


# Crypto Domain SSZ

class SigningData(Serializable):
    fields = [
        ('object_root', bytes32),
        ('domain', bytes32)
    ]


class ForkData(Serializable):
    fields = [
        ('current_version', bytes4),
        ('genesis_validators_root', bytes32),
    ]


def compute_fork_data_root(current_version: bytes, genesis_validators_root: bytes) -> bytes:
    """
    Return the appropriate ForkData root for a given deposit version.
    """
    if len(current_version) != 4:
        raise ValueError(f"Fork version should be in 4 bytes. Got {len(current_version)}.")
    return ForkData(
        current_version=current_version,
        genesis_validators_root=genesis_validators_root,
    ).hash_tree_root


def compute_deposit_domain(fork_version: bytes) -> bytes:
    """
    Deposit-only `compute_domain`
    """
    if len(fork_version) != 4:
        raise ValueError(f"Fork version should be in 4 bytes. Got {len(fork_version)}.")
    domain_type = DOMAIN_DEPOSIT
    fork_data_root = compute_deposit_fork_data_root(fork_version)
    return domain_type + fork_data_root[:28]


def compute_deposit_fork_data_root(current_version: bytes) -> bytes:
    """
    Return the appropriate ForkData root for a given deposit version.
    """
    genesis_validators_root = ZERO_BYTES32  # For deposit, it's fixed value
    return compute_fork_data_root(current_version, genesis_validators_root)


def compute_signing_root(ssz_object: Serializable, domain: bytes) -> bytes:
    """
    Return the signing root of an object by calculating the root of the object-domain tree.
    The root is the hash tree root of:
    https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#signingdata
    """
    if len(domain) != 32:
        raise ValueError(f"Domain should be in 32 bytes. Got {len(domain)}.")
    domain_wrapped_object = SigningData(
        object_root=ssz_object.hash_tree_root,
        domain=domain,
    )
    return domain_wrapped_object.hash_tree_root


class DepositMessage(Serializable):
    """
    Ref: https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#depositmessage
    """
    fields = [
        ('pubkey', bytes48),
        ('withdrawal_credentials', bytes32),
        ('amount', uint64),
    ]


class DepositData(Serializable):
    """
    Ref: https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#depositdata
    """
    fields = [
        ('pubkey', bytes48),
        ('withdrawal_credentials', bytes32),
        ('amount', uint64),
        ('signature', bytes96)
    ]


def signed_deposit(sk) -> DepositData:
    withdrawal_credentials = bytes.fromhex('01')
    withdrawal_credentials += b'\x00' * 11
    withdrawal_credentials += from_hex_string_to_bytes(variables.ACCOUNT.address[2:])

    deposit_message = DepositMessage(
        bls.SkToPk(sk),
        withdrawal_credentials,
        10 ** 9,
    )

    domain = compute_deposit_domain(fork_version=bytes.fromhex('01017000'))
    signing_root = compute_signing_root(deposit_message, domain)
    signed_deposit = DepositData(
        **deposit_message.as_dict(),
        signature=bls.Sign(
            sk,
            signing_root,
        )
    )
    return signed_deposit


if __name__ == '__main__':
    w3 = Web3(HTTPProvider('http://34.88.131.109:8545'))

    deposit_contract: DepositContract = cast(DepositContract, w3.eth.contract(
        address='0x4242424242424242424242424242424242424242',
        ContractFactoryClass=DepositContract,
    ))
    w3.attach_modules(
        {
            'lido': LidoContracts,
            'transaction': TransactionUtils,
        }
    )

    pk = int(from_hex_string_to_bytes('49c9ed78c4d5b13779351bf9afdb602ae95f1b3a25a6c543da663149953cf13f').hex(), 16)

    deposit_args = signed_deposit(pk)

    # Councils
    w3.provider.make_request('anvil_setBalance', ('0xF59a0EE75c3B378dd85c6316E3eC71EcaB71a175', hex(0)))
    w3.provider.make_request('anvil_setBalance', ('0xF9e02dFC135ED007F0e07e13Ce7A17353cb8c0E1', hex(0)))
    # Current acc
    w3.provider.make_request('anvil_setBalance', (variables.ACCOUNT.address, hex(321*10**18)))
    w3.provider.make_request('anvil_setBalance', (w3.lido.deposit_security_module.address, hex(1*10**18)))

    td = deposit_contract.functions.deposit(
        deposit_args.as_dict()['pubkey'],
        deposit_args.as_dict()['withdrawal_credentials'],
        deposit_args.as_dict()['signature'],
        deposit_args.hash_tree_root,
    ).build_transaction({
        'from': variables.ACCOUNT.address,
        'value': Web3.to_wei(1, 'ether'),
        'nonce': w3.eth.get_transaction_count(variables.ACCOUNT.address),
    })
    deposit_contract.events.DepositEvent.get_logs(fromBlock=1768134 - 1000, toBlock=1768134)

    signed_tx = w3.eth.account.sign_transaction(td, variables.ACCOUNT._private_key)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(w3.eth.get_transaction(tx_hash))

    lido: LidoContract = cast(LidoContract, w3.eth.contract(
        address=w3.lido.lido_locator.lido(),
        ContractFactoryClass=LidoContract,
    ))

    lido.functions.submit(variables.ACCOUNT.address).transact({'from': variables.ACCOUNT.address, 'value': 320*10**18})

    dt = lido.functions.deposit(10, 2, b'').transact({
        'from': w3.lido.lido_locator.deposit_security_module.address,
    })

    # db._send_deposit_tx(
    #     msg['blockNumber'],
    #     Hash32(bytes.fromhex(msg['blockHash'][2:])),
    #     Hash32(bytes.fromhex(msg['depositRoot'][2:])),
    #     msg['stakingModuleId'],
    #     msg['nonce'],
    #     b'',
    #     ((msg['signature']['r'], compute_vs(msg['signature']['v'], msg['signature']['s'])),),
    # )
