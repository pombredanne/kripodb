# Copyright 2016 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from intbitset import intbitset
from nose.tools import eq_
from mock import call, Mock

import kripodb.db as db


def test_adapt_intbitset():
    bs = intbitset([1, 3, 5, 8])

    result = db.adapt_intbitset(bs)

    expected = bs.fastdump()
    eq_(result, expected)


def test_convert_intbitset():
    bs = intbitset([1, 3, 5, 8])

    result = db.convert_intbitset(bs.fastdump())

    eq_(result, bs)


class TestFastInserter(object):
    def setUp(self):
        self.cursor = Mock()
        self.unit = db.FastInserter(self.cursor)

    def testWith(self):
        with self.unit:
            self.cursor.execute.assert_has_calls([call('PRAGMA journal_mode=WAL'),
                                                  call('PRAGMA synchronous=OFF')])

        self.cursor.execute.assert_has_calls([call('PRAGMA journal_mode=DELETE'),
                                              call('PRAGMA synchronous=FULL')])


class TestFragmentsDB(object):
    def setUp(self):
        self.fdb = db.FragmentsDb(':memory:')


class TestIntbitsetDictEmpty(object):
    def setUp(self):
        self.fdb = db.FingerprintsDb(':memory:')
        self.bitsets = db.IntbitsetDict(self.fdb, 100)
        self.bid = 'id1'
        self.bs = intbitset([1, 3, 5, 8])

    def tearDown(self):
        self.fdb.close()

    def test_default_number_of_bits(self):
        fdb = db.FingerprintsDb(':memory:')
        bitsets = db.IntbitsetDict(fdb)

        eq_(bitsets.number_of_bits, None)

    def test_get_number_of_bits(self):
        eq_(self.bitsets.number_of_bits, 100)

    def test_set_number_of_bits(self):
        self.bitsets.number_of_bits = 200

        eq_(self.bitsets.number_of_bits, 200)

    def test_delete_number_of_bits(self):
        del self.bitsets.number_of_bits

        eq_(self.bitsets.number_of_bits, None)

    def test_len_empty(self):
        eq_(len(self.bitsets), 0)

    def test_contains_false(self):
        assert 'id1' not in self.bitsets

    def test_update(self):
        other = {self.bid: self.bs}

        self.bitsets.update(other)

        result = {k: v for k, v in self.bitsets.iteritems()}
        eq_(result, other)


class TestIntbitsetDictFilled(object):
    def setUp(self):
        self.fdb = db.FingerprintsDb(':memory:')
        self.bitsets = db.IntbitsetDict(self.fdb, 100)
        self.bid = 'id1'
        self.bs = intbitset([1, 3, 5, 8])
        self.bitsets[self.bid] = self.bs

    def test_getitem(self):
        result = self.bitsets['id1']

        eq_(result, self.bs)

    def test_len_filled(self):
        eq_(len(self.bitsets), 1)

    def test_contains_true(self):
        assert 'id1' in self.bitsets

    def test_del(self):
        del self.bitsets['id1']

        eq_(len(self.bitsets), 0)

    def test_keys(self):
        result = self.bitsets.keys()

        expected = ['id1']
        eq_(result, expected)

    def test_iteritems(self):
        result = {k: v for k, v in self.bitsets.iteritems()}

        expected = {self.bid: self.bs}
        eq_(result, expected)

    def test_iteritems_startswith(self):
        self.bitsets['someid'] = self.bs

        result = {k: v for k, v in self.bitsets.iteritems_startswith('id')}

        expected = {self.bid: self.bs}
        eq_(result, expected)
        assert 'someid' not in result

    def test_itervalues(self):
        result = [v for v in self.bitsets.itervalues()]

        expected = [self.bs]
        eq_(result, expected)