# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020

import collections # deque    # could use a list
import time   # sleep
import zmq    # Context

from circuit import N_GATES, ALL_PARTIES
from config  import LOCAL_PORT, SYNC_DELAY

# ---------------------------------------------------------------------------

class Publisher():
  def __init__(self, party_no):
    self.party_no = party_no
    self.socket = zmq.Context().socket(zmq.PUB)
    self.socket.bind(f'tcp://*:{LOCAL_PORT+party_no}')

  def send(self, dest, msg):
    # send message (pickled object) to destination party
    self.socket.send_string(f'{dest:02}', flags=zmq.SNDMORE)
    self.socket.send_pyobj(self.party_no, flags=zmq.SNDMORE)
    self.socket.send_pyobj(msg)

class Subscriber():
  def __init__(self, party_no):
    self.party_no = party_no
    self.socket = zmq.Context().socket(zmq.SUB)
    self.socket.setsockopt_string(zmq.SUBSCRIBE, f'{party_no:02}')
    self.queues = {p: collections.deque() for p in ALL_PARTIES}
    for p in ALL_PARTIES:
       self.socket.connect(f'tcp://localhost:{LOCAL_PORT+p}')

  def receive(self, sender):
    # return next message from sender, keep receiving messages until 
    # match, queue any messages from other senders
    if self.queues[sender]:
      return self.queues[sender].popleft()
    while True:
      _our_party_no = self.socket.recv_string()
      msg_sender = self.socket.recv_pyobj()
      msg = self.socket.recv_pyobj()
      if msg_sender == sender:
        return msg
      self.queues[msg_sender].append(msg)

# ---------------------------------------------------------------------------

class Network():
  # networking - for sending and receiving shares between parties

  def __init__(self, party_no):
    # create party's TCP port
    self.publisher = Publisher(party_no)
    # wait for all party processes/TCP ports to be created
    time.sleep(SYNC_DELAY)
    # connect to other parties TCP ports
    self.subscriber = Subscriber(party_no)
    # wait for other parties to connect to this party
    time.sleep(1)
    # create buffer for received shares
    self.shares = {p: {g: None for g in range(1, N_GATES+2)}
                   for p in ALL_PARTIES}

  def send_share(self, share, src_gate, dest_party):
    # send share for gate to destination party
    # print(f"    Sending {share} from {self.publisher.party_no} to {dest_party} (gate {src_gate})")
    self.publisher.send(dest=dest_party, msg=(src_gate,share))

  def receive_share(self, src_party, src_gate):
    # return share from (party:gate), keep receiving shares until 
    # match, save any shares received from other (party:gate)'s
    if self.shares[src_party][src_gate] is not None:
      # print(f"    Receiving {self.shares[src_party][src_gate]} from {src_party} to {self.publisher.party_no} (gate {src_gate})")
      return self.shares[src_party][src_gate]

    while True:   # could use recursion instead
      msg_gate, msg_share = self.subscriber.receive(src_party)
      self.shares[src_party][msg_gate] = msg_share
      if self.shares[src_party][src_gate] is not None:
        # print(f"    Receiving {self.shares[src_party][src_gate]} from {src_party} to {self.publisher.party_no} (gate {src_gate})")
        return self.shares[src_party][src_gate]


