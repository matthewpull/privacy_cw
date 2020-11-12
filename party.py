import random

from circuit import N_PARTIES, PRIME, DEGREE, GATES, ZER, INP, ADD, MUL
from modprime import add, mul

OUTPUT_GATE = list(GATES.values())[-1][1]


def bgw_protocol(party_no, private_value, network):
    # Phase 1: Shamir Secret Sharing

    coef = [private_value]
    for _ in range(DEGREE):
        coef.append(random.randint(0, PRIME - 1))
    
    outputs = []
    for dest_party in range(1, N_PARTIES + 1):
        share = calc_poly(dest_party, coef)
        outputs.append(share)
        network.send_share(share, party_no, dest_party)
    
    # Phase 2: Receive shares & Evaluate Add / Mul Gates
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(remote_party, remote_party))

    # Evaluate result of gates using shares
    result = evaluate_gates(shares, network, party_no)

    # Broadcast outputs
    for dest_party in range(1, N_PARTIES + 1):
        network.send_share(result, OUTPUT_GATE, dest_party)
    
    # Receive outputs
    outputs = [0]
    for remote_party in range(1, N_PARTIES + 1):
        outputs.append(network.receive_share(remote_party, OUTPUT_GATE))
    
    # Phase 3: Use Legrange Interpolation to combine outputs
    secret = recombination(outputs, party_no)
    print(f"Party {party_no} output {secret}")
    

def recombination(values, party_no):
    delta_values = [0]
    for i in range(1, N_PARTIES + 1):
        acc = 1
        for j in range(1, DEGREE + 2):
            if i == j:
                continue
            acc *= j / (j-i)
        delta_values.append(acc)
    acc = 0
    for i in range(1, DEGREE + 2):
        acc += values[i] * delta_values[i]
    acc %= PRIME
    return acc


def calc_poly(x, coef):
    output = 0
    for i in range(len(coef)):
        output += coef[i] * (x ** i)
    return output % PRIME


def evaluate_gates(shares, network, party_no):
    results = {}
    for key, value in GATES.items():
        gate_type, connect_to, order = value
        if connect_to not in results:
            results[connect_to] = {1: None, 2: None}

        if gate_type == ZER:
            pass
        elif gate_type == INP:
            results[connect_to][order] = shares[key]
        elif gate_type == ADD:
            results[connect_to][order] = add(results[key][1], results[key][2])
        elif gate_type == MUL:
            results[connect_to][order] = multiply(results[key][1], results[key][2], key, network, party_no)
        else:
            print(f"Error. Unable to evaluate {gate_type} in key {key}")
    return results[OUTPUT_GATE][1]


def split_share(coef, src_gate, network):
    for _ in range(DEGREE):
        coef.append(random.randint(0, PRIME - 1))
    
    outputs = []
    for dest_party in range(1, N_PARTIES + 1):
        share = calc_poly(dest_party, coef)
        outputs.append(share)
        network.send_share(share, src_gate, dest_party)


def multiply(value_one, value_two, src_gate, network, party_no):
    # Compute locally compute d
    mult_secret = mul(value_one, value_two)

    # Party produces a poly and broadcast
    mult_coef = [mult_secret]
    split_share(mult_coef, src_gate, network)
    
    # Receive shares from others
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(remote_party, src_gate))

    delta_values = [0]
    for i in range(1, 2*DEGREE + 2):
        acc = 1
        for j in range(1, 2*DEGREE + 2):
            if i == j:
                continue
            acc *= j / (j-i)
        delta_values.append(acc)
    acc = 0
    for i in range(1, 2*DEGREE + 2):
        acc += shares[i] * delta_values[i]
    acc %= PRIME
    return acc
    
