from contextlib import contextmanager
import random
import sys


class NullFile:
    def flush(self):
        """Has no effect."""

    def write(self, string):
        """Writes here go nowhere."""


class RandomSeedIdempotent:
    _random_seed_called = False

    @classmethod
    def seed(cls):
        if not cls._random_seed_called:
            random.seed()
            cls._random_seed_called = True


def as_id_list(items):
    return ','.join(
        [
            str(item.pk) for item in items
        ]
    )


@contextmanager
def mute_stdout():
    stdout_old = sys.stdout
    sys.stdout = NullFile()
    yield
    sys.stdout = stdout_old
