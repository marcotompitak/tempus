from utils.validation import validate_ping, validate_tick
from utils.helpers import utcnow, standard_encode, mine, median_ts
from utils.common import logger, credentials, config
from utils.pki import sign
import time
import random
import threading
from utils.validation import validate_clockchain
import requests


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

    def copy_chain(self, peer_addr):
        logger.debug("Requesting chain from peer " + str(peer_addr))
        peer_url = self.networker.reverse_peers.get(peer_addr, None)

        if not peer_url:
            logger.debug("Peer unknown, aborting chain request")
            return False

        logger.debug("Requesting chain from netloc " + str(peer_url))
        r = requests.get(str(peer_url) + "/info/clockchain")

        try:
            alt_chain = r.json()['chain']
        except KeyError:
            logger.debug("Received invalid response from " + peer_addr + "; could not copy chain")
            return False

        alt_chain_is_valid = validate_clockchain(alt_chain)

        if alt_chain_is_valid:
            logger.debug("Received valid chain with " + str(len(alt_chain)) + " ticks")
            logger.debug("Clearing current chain")
            with self.clockchain.chain.mutex:
                self.clockchain.chain.queue.clear()
            logger.debug("Copying over new chain")
            for tick in alt_chain:
                logger.debug("Copying tick " + str(list(tick.keys())[0]))
                self.clockchain.chain.put(tick)
            logger.debug("Chain copied")

        logger.debug("Returning " + str(alt_chain_is_valid))
        return alt_chain_is_valid

    def resync(self):
        self.clockchain.lock = True
        alt_prev_ticks = list(set(tick['prev_tick'] for tick in self.clockchain.fork_pool.values()))
        logger.debug("Resyncing, alternative references found to ticks:")
        for ref in alt_prev_ticks:
            logger.debug(str(ref))

        if len(alt_prev_ticks) > 1:
            logger.debug("More than one alternative reference found, calculating majority")
            ref_counts = [(prev_tick, alt_prev_ticks.count(prev_tick)) for prev_tick in alt_prev_ticks]
            majority_prev_tick = sorted(ref_counts, key=lambda tup: tup[1], reverse=True)[0][0]
            logger.debug("Majority reference: " + str(majority_prev_tick))
        elif len(alt_prev_ticks) == 1:
            majority_prev_tick = alt_prev_ticks[0]
            logger.debug("One alternative reference found: " + str(majority_prev_tick))
        else:
            logger.debug("Asked to resync but there are no known alternative chains, aborting")
            return None

        majority_peers = [k for k, v in self.clockchain.fork_pool.items() if v['prev_tick'] == majority_prev_tick]
        logger.debug("Majority alternative reference represented by the following peers:")
        for peer in majority_peers:
            logger.debug(str(peer))

        logger.debug("Attempting to sync chain with majority peers")
        synced = False
        time.sleep(5) # Give other nodes a chance to finish their select stage before requesting their chain
        while not synced and len(majority_peers) > 0:
            next_peer = majority_peers.pop()
            logger.debug("Syncing with peer " + str(next_peer))
            synced = self.copy_chain(next_peer)

        if not synced:
            logger.debug("Attempted to resync but failed to obtain chain from any majority peer")
        else:
            self.clockchain.tick_pool.queue.clear()
            self.clockchain.fork_pool = {}
        self.clockchain.lock = False
        return synced

    def generate_and_process_ping(self, reference):
        # TODO: Code duplication between here and api.. where to put??
        # TODO: Can't be in helpers, and cant be in clockchain/networker..
        # Always construct ping in the following order:
        # 1) Init 2) Mine+nonce 3) Add signature
        # This is because the order of nonce and sig creation matters

        ping = {'pubkey': credentials.pubkey,
                'timestamp': utcnow(),
                'reference': reference}

        _, nonce = mine(ping)
        ping['nonce'] = nonce

        signature = sign(standard_encode(ping), credentials.privkey)
        ping['signature'] = signature

        # Validate own ping
        if not validate_ping(ping):
            logger.debug("Failed own ping validation")
            return False

        self.clockchain.add_to_ping_pool(ping)

        # Forward to peers (this must be after all validation)
        self.networker.forward(data_dict=ping, route='ping',
                               origin=credentials.addr,
                               redistribute=0)

        logger.debug("Forwarded own ping: " + str(ping))

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
                    synced = self.resync()
                    if not synced:
                        logger.debug("Sync failed, fingers crossed for next round")

                self.clockchain.select()
                self.networker.stage = 'ping'
