# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

# Circuit below to evalute
CIRCUIT = 3

# Gate types
INP, ADD, MUL = (0,1,2)

# Define MPC Function as an addition/multiplication circuit. INPut gates 
# precede ADD/MUL gates. ADD/MUL gates are defined in evaluation order. 
# By convention the final wire is considerd the circuit's output wire.

if CIRCUIT == 1: 	# example in Smart
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 2

  PRIVATE_VALUES = {1:20, 2:40, 3:21, 4:31, 5:1, 6:71}

  def function(x):	# function being evaluated by parties
    return (x[1]*x[2] + x[3]*x[4] + x[5]*x[6]) % PRIME

  GATES = {
    1:  (INP, 7, 1),
    2:  (INP, 7, 2),
    3:  (INP, 8, 1),
    4:  (INP, 8, 2),
    5:  (INP, 9, 1),
    6:  (INP, 9, 2),
    7:  (MUL, 10, 1),
    8:  (MUL, 10, 2),
    9:  (MUL, 11, 1),
    10: (ADD, 11, 2),
    11: (ADD, 12, 1),  	# (12,1) is circuit output wire
  }

elif CIRCUIT == 2:	# factorial tree for 2^n parties
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME = 100_003
  # PRIME = 1_000_000_007
  # PRIME = 35742549198872617291353508656626642567  # Large Bell prime

  # degree of polynominal - T in slides
  DEGREE = 2

  INPUTS = 2 ** 3
  PRIVATE_VALUES = {k: k for k in range(1, INPUTS+1)}

  def function(x):	# function being evaluated by parties
    product = 1
    for value in x.values(): product = (product * value) % PRIME
    return product

  GATES = {}

  def tree(next_gate, n_gates):
    global GATES
    if n_gates >= 1:
      kind = INP if next_gate == 1 else MUL
      output_gate = next_gate + n_gates
      last_gate = output_gate - 1
      for g in range(next_gate, output_gate, 2):
        GATES[g]   = (kind, output_gate, 1)
        if g < last_gate:
          GATES[g+1] = (kind, output_gate, 2)
        output_gate += 1
      tree(next_gate + n_gates, n_gates // 2)

  tree(1, INPUTS)


elif CIRCUIT == 3:	# Binary to decimal converter
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 100_003
  # degree of polynominal - T in slides
  DEGREE = 2

  # Binary number to be converted, as an array of digits (order unchanged)
  # Note - for large inputs, ensure MAX_TIME in config.py is increased
  INPUT = (1, 1, 0, 0, 1, 1, 0, 1)  # 205
  # INPUT = (1, 0, 1, 1, 0)  # 22
  # INPUT = (0, 1, 1, 0)  # 6
  # INPUT = [1 for _ in range(16)]  # 2^16 - 1 = 65535

  # Set up private values - input digits in order, then powers of two needed
  # for calculation
  PRIVATE_VALUES = {i+1: INPUT[i] for i in range(len(INPUT))}
  for i in range(1, len(INPUT)):
    PRIVATE_VALUES[i + len(INPUT)] = 2 ** (len(INPUT) - i)

  def function(x):	# function being evaluated by parties
    num_digits = len(x) // 2 + 1
    acc = x[num_digits]
    for i in range(1, num_digits):
      acc += x[i] * x[i + num_digits]
    return acc % PRIME
  
  # GATES_1_DIGIT = {
  #   1:  (INP, 2, 1),  # (2,1) is circuit output wire
  # }

  # GATES_2_DIGIT = {
  #   1:  (INP, 4, 1),
  #   2:  (INP, 5, 1),
  #   3:  (INP, 4, 2),
  #
  #   4:  (MUL, 5, 1),  # 4 * x[0]
  #
  #   5:  (ADD, 6, 1),  # (6,1) is circuit output wire
  # }

  # GATES_3_DIGIT = {
  #   1:  (INP, 6, 1),
  #   2:  (INP, 7, 1),
  #   3:  (INP, 9, 2),
  #   4:  (INP, 6, 2),
  #   5:  (INP, 7, 2),
  #
  #   6:  (MUL, 8, 1),  # 4 * x[0]
  #   7:  (MUL, 8, 2),  # 2 * x[1]
  #
  #   8:  (ADD, 9, 1),
  #   9:  (ADD, 10, 1),  # (10,1) is circuit output wire
  # }

  # GATES_4_DIGIT = {
  #   1:  (INP, 8, 1),
  #   2:  (INP, 9, 1),
  #   3:  (INP, 10, 1),
  #   4:  (INP, 13, 2),
  #   5:  (INP, 8, 2),
  #   6:  (INP, 9, 2),
  #   7:  (INP, 10, 2),
  #
  #   8:  (MUL, 11, 1),  # 8 * x[0]
  #   9:  (MUL, 11, 2),  # 4 * x[1]
  #   10: (MUL, 12, 2),  # 2 * x[2]
  #
  #   11:  (ADD, 12, 1),  # 100 + 0
  #   12:  (ADD, 13, 1),  # 100 + 1
  #   13:  (ADD, 14, 1),  # (14,1) is circuit output wire
  # }

  GATES = {}

  def calc_gates():
    num_input = len(INPUT)
    num_pv = len(PRIVATE_VALUES)

    # Input gates
    for i in range(1, num_input):
      GATES[i] = (INP, num_pv + i, 1)
    GATES[num_input] = (
      INP,
      2 * num_pv if num_input == 1 else 2 * num_pv - 1,
      1 if num_input == 1 else 2
    )
    for i in range(1, num_input):
      GATES[i + num_input] = (INP, i + num_pv, 2)
    
    # Multiply gates
    for i in range(1, num_input):
      GATES[i + num_pv] = (
        MUL,
        i + num_pv + num_input - 1 if i == 1 else i + num_pv + num_input - 2,
        1 if i == 1 else 2
      )
    
    # Add gates
    for i in range(1, num_input):
      GATES[i + num_pv + num_input - 1] = (
        ADD,
        i + num_pv + num_input,
        1
      )
  
  calc_gates()
  
# ___________________________________________________________________________ 

# true function result - used to check result from MPC circuit
FUNCTION_RESULT = function(PRIVATE_VALUES)

N_GATES     = len(GATES)
N_PARTIES   = len(PRIVATE_VALUES)
ALL_PARTIES = range(1, N_PARTIES+1)
ALL_DEGREES = range(1, DEGREE+1)

assert PRIME > N_PARTIES, "Prime > N failed :-("
assert 2*DEGREE < N_PARTIES, "2T < N failed :-("

# Various Primes 
# PRIME = 11
# PRIME = 101
# PRIME = 1_009
# PRIME = 10_007
# PRIME = 100_003
# PRIME = 1_000_003 
# PRIME = 1_000_000_007
# PRIME = 35742549198872617291353508656626642567  # Large Bell prime
