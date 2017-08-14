import ast
from bluesky.examples import motor
from bluesky.plans import scan
from bluesky.utils import install_qt_kicker
from bluesky.examples import motor, det3
from bluesky.plans import scan, SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
import time
import random


def test_hints(fresh_RE):
    RE = fresh_RE
    expected_hint = {'fields': [motor.name]}
    assert motor.hints() == expected_hint
    collector = []

    def collect(*args):
        collector.append(args)

    RE(scan([], motor, 1, 2, 2), {'descriptor': collect})
    name, doc = collector.pop()
    assert doc['hints'][motor.name] == expected_hint

now = time.time

class Detector:
    name = 'det'
    parent = None
    root = None

    def read(self):
        return {'a': {'value': random.random(), 'timestamp': now()},
                'b': {'value': random.random(), 'timestamp': now()}}

    def describe(self):
        return {'a': {'dtype': 'number', 'shape': (), 'source': ''},
                'b': {'dtype': 'number', 'shape': (), 'source': ''}}

    def read_configuration(self):
        return {}

    def describe_configuration(self):
        return {}

    def hints(self):
        return {'fields': ['a']}


def test_simple(fresh_RE):
    RE = fresh_RE
    det = Detector()
    bec = BestEffortCallback()
    RE.subscribe(bec)
    RE(scan([det], motor, 1, 5, 5))

def test_disable(fresh_RE):
    RE = fresh_RE
    det = Detector()
    bec = BestEffortCallback()
    RE.subscribe(bec)

    bec.disable()
    assert not bec.enabled

    RE(scan([det], motor, 1, 5, 5))
    assert bec._table is None

    bec.enable()
    assert bec.enabled

    RE(scan([det], motor, 1, 5, 5))
    assert bec._table is not None

    bec.peaks.com
    bec.peaks['com']
    assert ast.literal_eval(repr(bec.peaks)) == vars(bec.peaks)

    bec.clear()
    assert bec._table is None


def test_blank_hints(fresh_RE):
    RE = fresh_RE
    det = Detector()
    bec = BestEffortCallback()
    RE.subscribe(bec)
    RE(scan([det], motor, 1, 5, 5, md={'hints': {}}))


def test_with_baseline(fresh_RE):
    RE = fresh_RE
    det = Detector()
    bec = BestEffortCallback()
    RE.subscribe(bec)
    sd = SupplementalData(baseline=[det3])
    RE.preprocessors.append(sd)
    RE(scan([det], motor, 1, 5, 5))
