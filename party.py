import random

from circuit import N_PARTIES, PRIME, DEGREE, GATES, ADD, INP, MUL, ZER
from modprime import add, mul

def bgw_protocol(party_no, private_value, network):
    # Phase 1: Shamir Secret Sharing
    split_share(private_value, party_no, network)
    
    # Phase 2: Receive shares & Evaluate Add / Mul Gates
    shares = [0] # 0th elem is padding
    for i in range(1, N_PARTIES + 1):
        shares.append(network.receive_share(i, i))

    # Evaluate result of gates using shares
    output_gate_no = list(GATES.values())[-1][1]
    result = evaluate_gates(shares, network, output_gate_no)

    # Broadcast outputs
    for i in range(1, N_PARTIES + 1):
        network.send_share(result, output_gate_no, i)
    
    # Receive outputs
    outputs = [0]
    for i in range(1, N_PARTIES + 1):
        outputs.append(network.receive_share(i, output_gate_no))
    
    # Phase 3: Use Legrange Interpolation to combine outputs
    secret = recombination(outputs, DEGREE, party_no)
    print("Output: " + secret + " computed at party " + party_no)

def recombination(values, degree, party_no = None):
    deltas = [0]
    for i in range(1, degree + 2):
        count = 1
        for j in range(1, degree + 2):
            if i == j:
                continue
            count = count * j / (j-i)
        # Convert value to integer to prevent floating point issue
        count = int(count)
        deltas.append(count)
    count = 0
    for i in range(1, degree + 2):
        count += (values[i] * deltas[i])
    return count % PRIME

def get_poly_value(coefficients, x):
    output = 0
    for i in range(len(coefficients)):
        output += coefficients[i] * (x ** i)
    return output % PRIME

def evaluate_gates(shares, network, output_gate_no):
    outputs = [0]

    # First loop to set up output stucture
    for _ in range(len(GATES) + 1):
        outputs.append([0, 0, 0])
    
    # Second loop to do calculate values
    for i in GATES:
        type, connect_to, index = GATES[i]            

        if type == ZER:
            pass
        elif type == INP:
            outputs[connect_to][index] = shares[i]
        elif type == ADD:
            outputs[connect_to][index] = add(outputs[i][1], outputs[i][2])
        elif type == MUL:
            # Party produces a poly and broadcast
            split_share(mul(outputs[i][1], outputs[i][2]), i, network)
            # Receive shares from others
            shares = [0] # 0th elem is padding
            for j in range(1, N_PARTIES + 1):
                shares.append(network.receive_share(j, i))
            outputs[connect_to][index] = recombination(shares, DEGREE * 2)

    return outputs[output_gate_no][1]

def split_share(mult_secret, src_gate, network):
    coefficients = [mult_secret]
    for _ in range(DEGREE):
        coefficients.append(random.randint(1, PRIME - 1))
    
    for dest_party in range(1, N_PARTIES + 1):
        share = get_poly_value(coefficients, dest_party)
        network.send_share(share, src_gate, dest_party)
    
    
