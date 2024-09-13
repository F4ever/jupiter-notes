from providers.base import w3
from icontracts.curated_module import ICuratedModule
from network.deploys import *
import pdb


# c = w3.contract.load('0x5bF85BadDac33F91B38617c18a3F829f912Ca060')
# sr = c.load_contract('stakingRouter')
# print(repr(sr.functions.getStakingModules().call()))
# sr.pprint(sr.functions.getStakingModules().call())
# curated = w3.contract.load('0xE12ABf35fA6f69C97Cc0AcF67B38D3000435790e')

# nor = ICuratedModule(w3.contract.load('0xE12ABf35fA6f69C97Cc0AcF67B38D3000435790e'))
# nor.contract.pprint(nor.node_operators)

# print(w3.eth.get_block('latest'))
# mainnet_locator(w3)
# holesky_locator(w3)
# print(w3.eth.get_block('latest'))