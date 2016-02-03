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

import kripodb.script as script


def test_pairs_subcommand_defaults():
    parser = script.make_parser()

    args = parser.parse_args(['pairs', 'fp1', 'fp2', 'outfn'])

    eq_(args.func, script.pairs_run)

    fargs = vars(args)
    del(fargs['func'])
    expected = {
        'out_format': 'tsv',
        'cutoff': 0.45,
        'out_file': 'outfn',
        'fragmentsdbfn': None,
        'mean_onbit_density': 0.01,
        'precision': 65535,
        'nomemory': False,
        'fingerprintsfn2': 'fp2',
        'fingerprintsfn1': 'fp1'
    }
    eq_(fargs, expected)
