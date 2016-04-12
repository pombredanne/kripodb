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
from nose.tools import eq_
from pyramid import testing
from webtest import TestApp
from kripodb import webservice
from kripodb.hdf5 import DistanceMatrix
from kripodb.version import __version__


class TestWebservice(object):
    def setUp(self):
        self.matrix = DistanceMatrix('data/distances.h5')
        self.app = webservice.wsgi_app(self.matrix)

    def tearDown(self):
        self.matrix.close()

    def test_get_similar_fragments(self):
        fragment_id = '3j7u_NDP_frag24'
        cutoff = 0.85

        with self.app.app.test_request_context():
            result = webservice.get_similar_fragments(fragment_id, cutoff, 1000)
            expected = [
                {'query_frag_id': '3j7u_NDP_frag24', 'hit_frag_id': '3j7u_NDP_frag23', 'score': 0.8991},
            ]
            eq_(result, expected)

    def test_get_version(self):
        result = webservice.get_version()

        expected = {'version': __version__}
        eq_(result, expected)

    def test_wsgi_app(self):
        eq_(self.app.app.config['matrix'], self.matrix)
