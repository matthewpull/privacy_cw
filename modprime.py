# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

# arithmetic modulo a prime number

import functools # reduce
import random    # randint

from circuit2_electric_boogaloo import PRIME

# ---------------------------------------------------------------------------

def mod(a):
  return a % PRIME

def add(a, b):
  return (a + b) % PRIME

def sub(a, b):
  return (a - b) % PRIME

def mul(a, b):
  return (a * b) % PRIME

def inv(a):
  # compute multiplicative inverse (mod p) using fermat's little theorem 
  return pow(a, PRIME-2, PRIME)

def div(a, b):
  return mul(a, inv(b))

def randint():
  return random.randint(1, PRIME-1)

def summation(list):
  return functools.reduce(add, list)

def product(list):
  return functools.reduce(mul, list)

