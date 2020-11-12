# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

from config import VERBOSE

# ---------------------------------------------------------------------------

party_no = 0
line = 0

def init_logging(_party_no):
  global party_no, line
  party_no = _party_no
  line = 0

def write(message):
  global party_no, line
  line += 1
  print(f'{party_no:02}-{line:03}: {message}')

def debug(message, verbose=1):
  global party_num, line
  if VERBOSE >= verbose:
    print(f'{party_no:02}-{line:03}: {message}')

def dsort(dict):  # dictionary sorted on key
  return {k: v for (k,v) in sorted(dict.items())}

