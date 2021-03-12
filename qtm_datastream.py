
import asyncio
import qtm
import sys
from observer import *
import logging.config
from argparse import ArgumentParser
import array


async def setup(host_qtm, port_qtm, host_moticon, port_moticon):
    """ Main function """
    connection = await qtm.connect(host_qtm, port_qtm, timeout=None)

    pub = Publisher()
    watch_stop_n_go = Subscriber('watch_stop_n_go', host_moticon, port_moticon)
    pub.register(watch_stop_n_go)

    if connection is None:
        return

    #turn off logging from get_state()
    logging.config.dictConfig({
    'version': 1,
    # Other configs ...
    'disable_existing_loggers': True
    })

    while True:
        await observe_start_and_stop(connection, pub)


async def observe_start_and_stop(connection, pub):
    state = await connection.get_state()
    #state = None
    pub.dispatch(state)

#if __name__ == "__main__":
def stream():
    # parser = ArgumentParser(description="UDP qtm event sender")
    # parser.add_argument("--host_qtm", default="127.0.0.1", help="IP address of the network interface which machine is running qtm")
    # parser.add_argument("--port_qtm", default=22223, type=int, help="Listening port of machine running qtm")
    # parser.add_argument("--host_moticon", default="127.0.0.1", help="IP address of the receiving network interface running moticon")
    # parser.add_argument("--port_moticon", default=8888, type=int, help="Listening port of machine running moticon")
    # args = parser.parse_args()
    # asyncio.ensure_future(setup(host_qtm=args.host_qtm, port_qtm=args.port_qtm, host_moticon=args.host_moticon, port_moticon=args.port_moticon))
    asyncio.ensure_future(setup(host_qtm="127.0.0.1", port_qtm=22223, host_moticon="127.0.0.1", port_moticon=8888))
    asyncio.get_event_loop().run_forever()
