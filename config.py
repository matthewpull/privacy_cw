# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

# verbosity level useful for debugging (log.py)
VERBOSE = 0   # 0=quiet, 1+=increasing verbosity

# set to True to use party no as seed, useful for debugging (mpc.py)
REPEATABLE_RANDOM_NUMBERS = False

# optional - set to True if you write a non-distributed (non-multiprocess) 
#   version and wish to test (mpc.py)
LOCAL = False

# ---------------------------------------------------------------------------

# each party will open its own TCP port - at LOCAL_PORT+PartyNo (network.py)
#   change if it clashes with another service or you are running on a server
#   that others in the class are also using for the coursework - worth doing
#   if running on a CSG machine. alternatively mpc.py could generate a random 
#   high LOCAL_PORT and pass as a parameter when parties are created.
LOCAL_PORT = 12340

# increase following two timeouts if running on a slow or overloaded machine
#   all parties will be terminated after this number of seconds (mpc.py)
MAX_TIME = 5
# each party will sleep for this number of seconds before connecting to other
#   parties (network.py)
SYNC_DELAY = 2

# pkill pattern - used to kill zombie or runaway processes (Makefile, mpc.py)
PKILL_PATTERN = 'MPC_PROCESS'

