import logging

from selv import selv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@selv(logger=logger.info)
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1


counter = Counter()
counter.increment()
counter.increment()

print("Check console for logged changes above.")
