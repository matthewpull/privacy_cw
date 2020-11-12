import random

from circuit import N_PARTIES, PRIME, DEGREE, GATES, INP, ADD, MUL
from modprime import add, mul

OUTPUT_GATE = len(GATES) + 1

def bgw_protocol(party_no, private_value, network):
    # Phase 1: Shamir Secret Sharing
    coef = [private_value]
    # split_share(coef, party_no, network)
    for _ in range(DEGREE):
        coef.append(random.randint(0, PRIME - 1))
    
    outputs = []
    for dest_party in range(1, N_PARTIES + 1):
        share = calc_poly(dest_party, coef)
        outputs.append(share)
        network.send_share(share, party_no, dest_party)
    
    print(f"Party: {party_no}, Shares: {outputs}, Coef: {coef}")

    # Phase 2: Receive shares & Evaluate Add / Mul Gates
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        # !!!!!!!!! (╯°□°)╯︵ ┻━┻ !!!!!!!!! #
        # TODO: Remember to change received params
        # !!!!!!!!! (╯°□°)╯︵ ┻━┻ !!!!!!!!! #
        shares.append(network.receive_share(remote_party, remote_party))
    print(f"Party: {party_no} shares: {shares}")

    # Evaluate result of gates using shares
    result = evaluate_gates(shares, network)

    # Broadcast outputs
    for dest_party in range(1, N_PARTIES + 1):
        network.send_share(result, OUTPUT_GATE, dest_party)
    
    # Receive outputs
    outputs = [0]
    for remote_party in range(1, N_PARTIES + 1):
        outputs.append(network.receive_share(remote_party, OUTPUT_GATE))
    
    # Phase 3: Use Legrange Interpolation to combine outputs
    secret = recombination(outputs, party_no)
    

def recombination(values, party_no = None):
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
    print(f"Party {party_no} acc: {acc} delta_values: {delta_values} values: {values}")
    return acc

def calc_poly(x, coef):
    output = 0
    for i in range(len(coef)):
        output += coef[i] * (x ** i)
    return output % PRIME

def evaluate_gates(shares, network):
    results = {}
    for key, value in GATES.items():
        gate_type, connect_to, order = value
        if connect_to not in results:
            results[connect_to] = {1: None, 2: None}

        if gate_type == INP:
            results[connect_to][order] = shares[key]
        elif gate_type == ADD:
            results[connect_to][order] = add(results[key][1], results[key][2])
            # print(f"Adding {results[key][1]} + {results[key][2]} to gate {connect_to}")
        elif gate_type == MUL:
            results[connect_to][order] = multiply(results[key][1], results[key][2], key, network)
            
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
    
    print(f"Party: {src_gate}, Shares: {outputs}, Coef: {coef}")

def multiply(value_one, value_two, src_gate, network):
    # Compute locally compute d
    mult_secret = mul(value_one, value_two)

    # Party produces a poly and broadcast
    mult_coef = [mult_secret]
    # split_share(mult_coef, src_gate, network)
    for _ in range(DEGREE):
        mult_coef.append(random.randint(0, PRIME - 1))
    
    outputs = []
    for dest_party in range(1, N_PARTIES + 1):
        share = calc_poly(dest_party, mult_coef)
        outputs.append(share)
        network.send_share(share, src_gate, dest_party)
    
    print(f"Gate: MUL, Value one: {value_one}, Value two: {value_two}, Shares: {outputs}, Coef: {mult_coef}")

    # Receive shares from others
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(remote_party, src_gate))

    print(f"Received shares: {shares}")

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
        acc += shares[i] * delta_values[i]
    acc %= PRIME
    print(f"Party Mult acc: {acc} delta_values: {delta_values} values: {shares}")
    return acc
    
