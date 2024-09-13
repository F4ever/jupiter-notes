DEVNET1_LOCATOR = '0x3F8ae3A6452DC4F7df1E391df39618a9aCF715A6'
HOLESKY_LOCATOR = '0x28FAB2059C713A7F9D8c86Db49f9bb0e96Af1ef8'
MAINNET_LOCATOR = '0xC1d0b3DE6792Bf6b4b37EccdcC24e45978Cfd2Eb'


def devnet1_locator(w3):
    w3.holesky()
    return w3.contract.load(DEVNET1_LOCATOR)


def holesky_locator(w3):
    w3.holesky()
    return w3.contract.load(HOLESKY_LOCATOR)


def mainnet_locator(w3):
    w3.mainnet()
    return w3.contract.load(MAINNET_LOCATOR)
