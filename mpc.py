# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

import random     # seed
import subprocess # Popen
import sys        # argv
import time       # sleep

from circuit2_electric_boogaloo import ALL_PARTIES, CIRCUIT, N_PARTIES, PRIVATE_VALUES
from config  import LOCAL, MAX_TIME, PKILL_PATTERN, REPEATABLE_RANDOM_NUMBERS
from log     import init_logging
from party2_electric_boogaloo   import bgw_protocol
from network import Network

# from local import simulate_parties

# ---------------------------------------------------------------------------

def main():
  print(f'CIRCUIT {CIRCUIT}')

  # create MPC party processes
  parties = {}
  for p in ALL_PARTIES:	# to randomise Popens use 'for' on next line instead
  # for p in random.sample(ALL_PARTIES, k=N_PARTIES):
    parties[p] = subprocess.Popen(['python3','mpc.py', str(p), PKILL_PATTERN],
                 bufsize=1, text=True)   # line buffered text output

  # politely terminate all processes after max_time (sends SIGTERM signal)
  time.sleep(MAX_TIME)
  for p in ALL_PARTIES:
    parties[p].terminate()

# ---------------------------------------------------------------------------

if LOCAL:
  # optional - code for non-distributed circuit evaluation
  # simulate_parties()
  pass
elif len(sys.argv) > 1:
  # code for MPC party process
  party_no = int(sys.argv[1])

  if REPEATABLE_RANDOM_NUMBERS:
    random.seed(party_no)

  init_logging(party_no)
  network = Network(party_no)
  bgw_protocol(party_no, PRIVATE_VALUES[party_no], network)

else:
  # code for top-level process - creates and terminates MPC parties
  main()


