import random

from circuit import N_PARTIES, PRIME, DEGREE, GATES, ADD, INP, MUL, ZER
from modprime import add, mul

PARTY_NO = None

def bgw_protocol(party_no, private_value, network):
    global PARTY_NO
    PARTY_NO = party_no
    # Phase 1: Shamir Secret Sharing

    coefficients = [private_value]
    for _ in range(DEGREE):
        coefficients.append(random.randint(0, PRIME - 1))
    
    outputs = []
    for dest_party in range(1, N_PARTIES + 1):
        share = get_poly_value(coefficients, dest_party)
        outputs.append(share)
        network.send_share(share, party_no, dest_party)
    
    # Phase 2: Receive shares & Evaluate Add / Mul Gates
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(remote_party, remote_party))

    # Evaluate result of gates using shares
    output_gate_no = list(GATES.values())[-1][1]
    result = evaluate_gates(shares, network, party_no, output_gate_no)

    # Broadcast outputs
    for dest_party in range(1, N_PARTIES + 1):
        network.send_share(result, output_gate_no, dest_party)
    
    # Receive outputs
    outputs = [0]
    for remote_party in range(1, N_PARTIES + 1):
        outputs.append(network.receive_share(remote_party, output_gate_no))
    
    # Phase 3: Use Legrange Interpolation to combine outputs
    secret = recombination(outputs, DEGREE, party_no)
    print(f"Party {party_no} output {secret}")

def recombination(values, degree, party_no = None):
    deltas = [0]
    for i in range(1, degree + 2):
        count = 1
        for j in range(1, degree + 2):
            if i == j:
                continue
            count = count * j / (j-i)
        deltas.append(count)
    count = 0
    for i in range(1, degree + 2):
        count = count + (values[i] * deltas[i])
    count = count % PRIME
    return count

def get_poly_value(coefficients, x):
    output = 0
    for i in range(len(coefficients)):
        output = output + coefficients[i] * (x ** i)
    return output % PRIME

def evaluate_gates(shares, network, party_no, output_gate_no):
    outputs = [0]

    # First loop to set up output stucture
    for _ in range(len(GATES) + 1):
        outputs.append([0, 0, 0])
    
    # Second loop to do calculate values
    for i in GATES:
        gate_type, connect_to, index = GATES[i]            

        if gate_type == ZER:
            pass
        elif gate_type == INP:
            outputs[connect_to][index] = shares[i]
        elif gate_type == ADD:
            outputs[connect_to][index] = add(outputs[i][1], outputs[i][2])
        elif gate_type == MUL:
            outputs[connect_to][index] = multiply(outputs[i][1], outputs[i][2], i, network, party_no)
    return outputs[output_gate_no][1]

def split_share(mult_secret, src_gate, network):
    coefficients = [mult_secret]
    for _ in range(DEGREE):
        coefficients.append(random.randint(0, PRIME - 1))
    
    for dest_party in range(1, N_PARTIES + 1):
        share = get_poly_value(coefficients, dest_party)
        network.send_share(share, src_gate, dest_party)

def multiply(value_one, value_two, src_gate, network, party_no):
    # Compute locally compute d
    # Party produces a poly and broadcast
    split_share(mul(value_one, value_two), src_gate, network)
    
    # Receive shares from others
    shares = [0] # 0th elem is padding
    for remote_party in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(remote_party, src_gate))

    return recombination(shares, DEGREE * 2)
    
