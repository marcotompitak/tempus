from utils.validation import validate_ping, validate_tick
from utils.helpers import utcnow, standard_encode, mine, median_ts
from utils.common import logger, credentials, config
from utils.pki import sign
import time
import random
import threading


class Timeminer(object):
    def __init__(self, clockchain, networker):

        self.clockchain = clockchain
        self.networker = networker
        self.added_ping = False
        self.ping_thread = threading.Thread(target=self.ping_worker)
        self.tick_thread = threading.Thread(target=self.tick_worker)
        self.select_thread = threading.Thread(target=self.select_worker)
        self.ping_thread.start()
        self.tick_thread.start()
        self.select_thread.start()

    def generate_and_process_ping(self, reference, vote=False):
        # TODO: Code duplication between here and api.. where to put??
        # TODO: Can't be in helpers, and cant be in clockchain/networker..
        # Always construct ping in the following order:
        # 1) Init 2) Mine+nonce 3) Add signature
        # This is because the order of nonce and sig creation matters

        ping = {'pubkey': credentials.pubkey,
                'timestamp': utcnow(),
                'reference': reference}

        stage = 'vote' if vote else 'ping'

        _, nonce = mine(ping)
        ping['nonce'] = nonce

        signature = sign(standard_encode(ping), credentials.privkey)
        ping['signature'] = signature

        # Validate own ping
        if not validate_ping(ping, self.clockchain.ping_pool, vote):
            logger.debug("Failed own " + stage + " validation")
            return False

        if vote:
            self.clockchain.add_to_vote_pool(ping)
        else:
            self.clockchain.add_to_ping_pool(ping)

        route = 'vote' if vote else 'ping'

        # Forward to peers (this must be after all validation)
        self.networker.forward(data_dict=ping, route=route,
                               origin=credentials.addr,
                               redistribute=0)

        logger.debug("Forwarded own " + route + ": " + str(ping))

        return True

    def generate_and_process_tick(self):
        height = self.clockchain.current_height() + 1

        tick = {
            'list': list(self.clockchain.ping_pool.values()),
            'pubkey': credentials.pubkey,
            'prev_tick': self.clockchain.prev_tick_ref(),
            'height': height
        }

        this_tick, nonce = mine(tick)

        tick['nonce'] = nonce

        signature = sign(standard_encode(tick), credentials.privkey)
        tick['signature'] = signature

        # This is to keep track of the "name" of the tick as debug info
        # this_tick is not actually necessary according to tick schema
        tick['this_tick'] = this_tick

        prev_tick = self.clockchain.latest_selected_tick()

        # Validate own tick
        if validate_tick(tick, prev_tick, verbose=True):
            self.clockchain.add_to_tick_pool(tick)
            # Forward to peers (this must be after all validation)
            self.networker.forward(data_dict=tick, route='tick',
                                   origin=credentials.addr,
                                   redistribute=0)
            logger.debug("Forwarded own tick: " + str(tick))
            self.clockchain.ping_pool = {}
            self.added_ping = False
            return True

        logger.debug("Failed own tick validation, not forwarded")
        return False

    def ping_worker(self):
        while True:
            if self.networker.ready and not self.added_ping and not self.networker.stage == 'select' \
                    and not self.clockchain.lock:

                self.networker.stage = "ping"

                logger.debug("Ping stage--------------------------------------")
                successful = \
                    self.generate_and_process_ping(
                        self.clockchain.prev_tick_ref())

                if not successful:
                    continue

                self.added_ping = True
            else:
                time.sleep(1)

    def tick_worker(self):
        while True:
            time.sleep(5)
            if self.networker.ready \
                    and not self.clockchain.lock:

                if len(list(self.clockchain.ping_pool.values())) == 0:
                    logger.info("(tick_worker) No pings, waiting")
                    continue

                logger.info("(tick_worker) Pingpool not empty, building tick")

                self.generate_and_process_tick()
                self.networker.stage = 'select'

    def select_worker(self):
        while True:
            time.sleep(5)
            if self.clockchain.tick_pool_size() > 0 \
                    and not self.clockchain.lock:
                self.networker.stage = 'select'
                logger.debug("Select stage--------------------------------------")
                grace_period = 10
                time.sleep(grace_period)

                logger.debug("Number of ticks: " + str(self.clockchain.tick_pool_size()))
                logger.debug("Number of forks: " + str(self.clockchain.fork_pool_size()))

                if self.clockchain.fork_pool_size() > self.clockchain.tick_pool_size():
                    logger.debug("Detected we're on minority fork, syncing")
                    self.clockchain.synced = False
                    synced = self.clockchain.resync()
                    if not synced:
                        logger.debug("Sync failed, fingers crossed for next round")

                self.clockchain.select()
                self.networker.stage = 'ping'
