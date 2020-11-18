# Written by Matthew Pull (mp1816) and Alvin Lee (aml1817)
import random

from log import init_logging, write, debug
from modprime import randint, add, mul, div
from circuit2_electric_boogaloo import GATES, N_PARTIES, ALL_PARTIES, INP, ADD, MUL, PRIME, DEGREE

OUTPUT_GATE = len(GATES) + 1
N_INPUTS = sum([1 for (gate_type, _, _) in GATES.values() if gate_type == INP])
RECOMBINATION_VECTOR_CACHE = {}
NO_RANDOM = False


def bgw_protocol(party_no, private_value, network):
    if NO_RANDOM:
        # Force a known set of "random" numbers for debug purposes
        random.seed(party_no)
    init_logging(party_no)
    initial_shares = bgw_step_one(party_no, network, private_value) 
    circuit_result = bgw_step_two(network, initial_shares)
    result = bgw_step_three(network, circuit_result)
    write(f"Final result is {result}")


# Step One - Distribute private inputs & split shares
def bgw_step_one(party_no, network, private_value):
    # Generate random polynomial
    local_coeff = [private_value] + [randint() for _ in range(DEGREE)]
    debug(f"Polynomial coefficients (ascending powers of x): {local_coeff}")
    
    # Split private inputs
    if (party_no <= N_INPUTS):
        shares = []
        for dest_party in ALL_PARTIES:
            share = calc_poly(dest_party, local_coeff)
            shares.append(share)
            network.send_share(share, party_no, dest_party)
        debug(f"Calculated shares: {shares}")
    
    # Distribute shares
    shares = {
        remote_party: network.receive_share(remote_party, remote_party) 
        for remote_party in range(1, N_INPUTS + 1)
    }

    debug(f"Received shares: {list(shares.values())}")
    return shares


# Step Two - Evaluate circuit
def bgw_step_two(network, shares):
    results = {}
    for key, (gate_type, output_gate, order) in GATES.items():
        if not output_gate in results:
            results[output_gate] = {1: None, 2: None}
        if gate_type == INP:
            results[output_gate][order] = shares[key]
        elif gate_type == ADD:
            add_result = add(results[key][1], results[key][2])
            results[output_gate][order] = add_result
            debug(f"Calculating gate {key} (ADD): {results[key][1]} + {results[key][2]} (mod {PRIME}) = {add_result}")
        elif gate_type == MUL:
            results[output_gate][order] = multiply(network, results[key][1], results[key][2], key)
        else:
            write(f"Error. Unable to evaluate {gate_type} in key {key}")
    return results[OUTPUT_GATE][1]


# Step Three - Broadcast outputs & combine outputs
def bgw_step_three(network, result):
    # Broadcast output
    for dest_party in ALL_PARTIES:
        network.send_share(result, OUTPUT_GATE, dest_party)
    
    # Receive outputs
    outputs = {
        remote_party: network.receive_share(remote_party, OUTPUT_GATE)
        for remote_party in ALL_PARTIES
    }

    # Combine outputs
    recombination_vector = calc_recombination_vector(DEGREE + 1) 
    result = sum([
        outputs[i] * recombination_vector[i]
        for i in range(1, len(recombination_vector) + 1)
    ]) % PRIME
    
    debug(f"Final result {result} using rec vector {recombination_vector}")
    return result


# Calculate recombination vector and cache it
def calc_recombination_vector(size):
    if size in RECOMBINATION_VECTOR_CACHE:
        return RECOMBINATION_VECTOR_CACHE[size]

    recombination_vector = {}
    for i in range(1, size + 1):
        acc = 1
        for j in [x for x in range(1, size + 1) if i != x]:
            acc = mul(acc, div(j, j-i))
        recombination_vector[i] = int(acc)
    
    RECOMBINATION_VECTOR_CACHE[size] = recombination_vector
    return recombination_vector

# Calculate Poly(x)
def calc_poly(x, coeff):
    return sum([coeff[i] * (x ** i) for i in range(len(coeff))]) % PRIME


# Runs the multiplication protocol with sharing
def multiply(network, a, b, src_gate):
    # Begin with locally computing (a x b) % prime
    private_value = mul(a, b)
    debug(f"Calculating gate {src_gate} (MUL): {a} x {b} (mod {PRIME}) = {private_value}")

    # Party produces a new polynomial and broadcasts it
    local_coeff = [private_value] + [randint() for _ in range(DEGREE)]
    debug(f"Coefficients for gate {src_gate} (MUL): {local_coeff}")
    shares = []
    for dest_party in ALL_PARTIES:
        share = calc_poly(dest_party, local_coeff)
        shares.append(share)
        network.send_share(share, src_gate, dest_party)
    debug(f"Calculated shares for gate {src_gate} (MUL): {shares}")

    # Receive shares from others
    shares = {
        remote_party: network.receive_share(remote_party, src_gate) 
        for remote_party in ALL_PARTIES
    }
    debug(f"Received shares for gate {src_gate} (MUL): {list(shares.values())}")

    recombination_vector = calc_recombination_vector(2*DEGREE + 1)

    result = sum([
        shares[i] * recombination_vector[i] for i in range(1, len(recombination_vector) + 1)
    ]) % PRIME
    debug(f"MUL gate {src_gate} result {result} using rec vector {recombination_vector}")
    return result
