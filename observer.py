import qtm
import logging.config
import sys
from udp_input import *

"""
    Classes which implement the design pattern observer
    subscriber = observable
    publisher = oberserver
    observer observers qtm and updates the observable about its state changes
    in this particular case the observable only reacts to EventCaptureStarted
    and EventCaptureStopped
"""

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

class Subscriber:
    def __init__(self, name, host_moticon, port_moticon):
        self.name = name
        self.prev_state = None
        self.host_moticon = host_moticon
        self.port_moticon = port_moticon
    def update(self, state):
        if self.prev_state != state:
            if(state == qtm.QRTEvent.EventCaptureStarted):
                send_udp(self.host_moticon, self.port_moticon, "1")
            elif(state == qtm.QRTEvent.EventCaptureStopped):
                send_udp(self.host_moticon, self.port_moticon, "0")
            self.prev_state = state


class Publisher:
    def __init__(self):
        self.subscribers = set()
    def register(self, who):
        self.subscribers.add(who)
    def unregister(self, who):
        self.subscribers.discard(who)
    def dispatch(self, state):
        for subscriber in self.subscribers:
            subscriber.update(state)
