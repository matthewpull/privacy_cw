from modprime import randint, add, mul
from circuit2_electric_boogaloo import GATES, N_PARTIES, INP, ADD, MUL, PRIME, DEGREE

OUTPUT_GATE = len(GATES) + 1

N_INPUTS = sum([1 for (gate_type, _, _) in GATES.values() if gate_type == INP])

recombination_vector_cache = {}

def bgw_protocol(party_no, private_value, network):
    initial_shares = bgw_step_one(party_no, network, private_value) 
    
    circuit_result = bgw_step_two(party_no, network, initial_shares)

    result = bgw_step_three(party_no, network, circuit_result)
    print(f"Party {party_no} - Result {result}")


# Step One - Distribute private inputs & split shares
def bgw_step_one(party_no, network, private_value):
    # Generate random polynomial
    local_coeff = [private_value] + [randint() for _ in range(DEGREE)]
    
    # Split private inputs
    if (party_no <= N_INPUTS):
        for dest_party in range(1, N_PARTIES + 1):
            share = calc_poly(dest_party, local_coeff)
            network.send_share(share, party_no, dest_party)
    
    # Distribute shares
    shares = {
        remote_party: network.receive_share(remote_party, remote_party) 
        for remote_party in range(1, N_INPUTS + 1)
    }

    print(f"Party: {party_no} shares: {shares}")

    return shares


# Step Two - Evaluate circuit
def bgw_step_two(party_no, network, shares):
    results = {}
    for key, (gate_type, output_gate, order) in GATES.items():
        if not output_gate in results:
            results[output_gate] = {1: None, 2: None}
        if gate_type == INP:
            results[output_gate][order] = shares[key]
        elif gate_type == ADD:
            results[output_gate][order] = add(results[key][1], results[key][2])
        elif gate_type == MUL:
            results[output_gate][order] = multiply(network, results[key][1], results[key][2], key)
        else:
            print(f"Error. Unable to evaluate {gate_type} in key {key}")
    return results[OUTPUT_GATE][1]


# Step Three - Broadcast outputs & combine outputs
def bgw_step_three(party_no, network, result):
    # Broadcast output
    for dest_party in range(1, N_PARTIES + 1):
        network.send_share(result, OUTPUT_GATE, dest_party)
    
    # Receive outputs
    outputs = {
        remote_party: network.receive_share(remote_party, OUTPUT_GATE)
        for remote_party in range(1, N_PARTIES + 1)
    }

    # Combine outputs
    recombination_vector = calc_recombination_vector(DEGREE + 1)
    result = sum([
        outputs[i] * recombination_vector[i]
        for i in range(1, len(recombination_vector) + 1)
    ])
    print(f"Party {party_no} cache {recombination_vector_cache}")
    return result % PRIME

# Calculate recombination vector and cache it
def calc_recombination_vector(size):
    if size in recombination_vector_cache:
        return recombination_vector_cache[size]

    recombination_vector = {}
    for i in range(1, size + 1):
        acc = 1
        for j in [x for x in range(1, size + 1) if i != x]:
            acc *= j / (j - i)
        recombination_vector[i] = int(acc)
    
    recombination_vector_cache[size] = recombination_vector
    return recombination_vector

# Calculate Poly(x)
def calc_poly(x, coeff):
    return sum([coeff[i] * (x ** i) for i in range(len(coeff))]) % PRIME


def multiply(network, a, b, src_gate):
    # Compute locally compute d
    print(f"mul {a}, {b}")
    private_value = mul(a, b)

    # Party produces a poly and broadcast
    local_coeff = [private_value] + [randint() for _ in range(DEGREE)]
    for dest_party in range(1, N_PARTIES + 1):
        share = calc_poly(dest_party, local_coeff)
        network.send_share(share, src_gate, dest_party)
    
    # Receive shares from others
    shares = {
        remote_party: network.receive_share(remote_party, src_gate) 
        for remote_party in range(1, N_PARTIES + 1)
    }

    recombination_vector = calc_recombination_vector(2*DEGREE + 1)

    result = sum([
        shares[i] * recombination_vector[i] for i in range(1, len(recombination_vector) + 1)
    ])
    return result
