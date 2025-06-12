import json
from eth2spec.phase0 import spec as phase0
from eth2spec.utils.ssz.ssz_impl import hash_tree_root, pack
from eth2spec.utils.merkle.minimal import get_merkle_proof
from eth2spec.test.helpers.state import get_sample_state

# Load state from file or REST API
def load_beacon_state(state_file_path: str):
    with open(state_file_path, 'r') as f:
        raw = json.load(f)
    state = phase0.BeaconState.decode_bytes(bytes.fromhex(raw['data']['root']))
    return state

# Get proof for a validator's balance
def generate_balance_proof(state: phase0.BeaconState, validator_index: int):
    # Get root of full state
    state_root = hash_tree_root(state)

    # Get the proof for validator's balance
    balance_tree = phase0.BeaconState.balances.get_backing(state)
    balance_proof = get_merkle_proof(balance_tree, validator_index, phase0.BeaconState.balances.length)

    # You could also generate validator proof like this:
    validator_tree = phase0.BeaconState.validators.get_backing(state)
    validator_proof = get_merkle_proof(validator_tree, validator_index, phase0.BeaconState.validators.length)

    return {
        "state_root": state_root.hex(),
        "validator_index": validator_index,
        "balance": state.balances[validator_index],
        "balance_proof": [p.hex() for p in balance_proof],
        "validator": state.validators[validator_index].hash_tree_root().hex(),
        "validator_proof": [p.hex() for p in validator_proof],
    }

# Example usage
if __name__ == "__main__":
    state = get_sample_state(phase0)  # You can also load a real one with load_beacon_state()
    validator_index = 0
    proof = generate_balance_proof(state, validator_index)

    print("Validator balance Merkle proof:")
    print(json.dumps(proof, indent=2))