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

import logging
import tables

from modifiedtanimoto import distances, corrections
from kripodb.db import FingerprintsDb, FragmentsDb


def dump_pairs(bitsets1,
               bitsets2,
               out_format,
               out_file,
               out,
               number_of_bits,
               mean_onbit_density,
               cutoff,
               label2id,
               precision,
               memory):
    """Dump pairs of bitset collection

    :param bitsets1: dictionary of bitset identifier as key
        and a intbitset object as value
    :param bitsets2: dictionary of bitset identifier as key
        and a intbitset object as value
    :param out_format:
    :param out_file:
    :param out:
    :param number_of_bits: Maximum number of bits in bitset
    :param mean_onbit_density:
    :param cutoff:
    :param id2label_file: dict to translate label to id (string to int)
    :param precision:
    :param memory:
    :return:
    """
    if out_file == '-' and out_format.startswith('hdf5'):
        raise Exception("hdf5 formats can't be outputted to stdout")

    if memory:
        # load whole dict in memory so it can be reused for each bitset1
        # deserialization of bitsets2 is only done one time
        bitsets2 = {k: v for k, v in bitsets2.iteritems()}

    expectedrows = len(bitsets1) * len(bitsets2) * cutoff * 0.025

    (corr_st, corr_sto) = corrections(mean_onbit_density)

    logging.warn('Generating pairs')

    distances_iter = distances(bitsets1, bitsets2,
                               number_of_bits, corr_st, corr_sto,
                               cutoff)

    if out_format == 'tsv':
        dump_pairs_tsv(distances_iter, out)
    elif out_format == 'tsv_compact':
        dump_pairs_tsv_compact(distances_iter,
                               label2id, precision,
                               out)
    elif out_format == 'hdf5':
        dump_pairs_hdf5(distances_iter, expectedrows, out_file)
    elif out_format == 'hdf5_compact':
        dump_pairs_hdf5_compact(distances_iter,
                                label2id, precision,
                                expectedrows,
                                out_file)
    else:
        raise LookupError('Invalid output format')


def dump_pairs_tsv(distances_iter, out):
    """Dump pairs as

    Pro:
    * when stored in sqlite can be used outside of Python
    Con:
    * big, unless output is compressed

    :param distances_iter:
    :param out:
    :return:

    """
    for label1, label2, distance in distances_iter:
        out.write('{}\t{}\t{}\n'.format(label1, label2, distance))


def dump_pairs_tsv_compact(distances_iter,
                           label2id, precision,
                           out):
    """
    Pro:
    * more compact, because label string is replaced with a integer
    * when stored in sqlite can be used outside of Python
    Con:
    * Requires a lookup table

    :param distances_iter:
    :param label2id: dict to translate label to id (string to int)
    :param precision:
    :param out:
    :return:
    """
    for label1, label2, distance in distances_iter:
        id1 = label2id[label1]
        id2 = label2id[label2]
        cd = int(distance * precision)
        out.write('{}\t{}\t{}\n'.format(id1, id2, cd))


class Pair(tables.IsDescription):
    a = tables.StringCol(15)
    b = tables.StringCol(15)
    score = tables.Float32Col()


def dump_pairs_hdf5(distances_iter, expectedrows, out_file):
    """
    Pro:
    * small
    * index on pair ids
    Con:
    * requires hdf5 library to access

    :param distances_iter:
    :param out_file:
    :return:
    """
    filters = tables.Filters(complevel=6, complib='blosc')
    h5file = tables.open_file(out_file, mode='w', filters=filters)
    table = h5file.create_table('/', 'pairs', Pair, 'Distance pairs', expectedrows=expectedrows)
    hit = table.row
    for label1, label2, distance in distances_iter:
        hit['a'] = label1
        hit['b'] = label2
        hit['score'] = distance
        hit.append()
    table.flush()
    table.cols.a.create_index(filters=filters)
    table.cols.b.create_index(filters=filters)
    h5file.close()


class PairCompact(tables.IsDescription):
    a = tables.UInt32Col()
    b = tables.UInt32Col()
    score = tables.UInt16Col()


def dump_pairs_hdf5_compact(distances_iter,
                            label2id, precision,
                            expectedrows,
                            out_file):
    """

    Pro:
    * very small, 9 bytes for each pair
    * index on pair ids
    Con:
    * requires hdf5 library to access
    * Requires a lookup table

    :param distances_iter:
    :param label2id: dict to translate label to id (string to int)
    :param precision:
    :param expectedrows:
    :param out_file:
    :return:
    """
    filters = tables.Filters(complevel=6, complib='blosc')
    h5file = tables.open_file(out_file, mode='w', filters=filters)
    table = h5file.create_table('/',
                                'pairs',
                                PairCompact,
                                'Distance pairs',
                                expectedrows=expectedrows)
    table.attrs['score_precision'] = precision
    hit = table.row
    for label1, label2, distance in distances_iter:
        hit['a'] = label2id[label1]
        hit['b'] = label2id[label2]
        hit['score'] = int(distance * precision)
        hit.append()
    table.cols.a.create_index(filters=filters)
    table.cols.b.create_index(filters=filters)
    h5file.close()


def distance2query(fingerprintsdb, query, out, mean_onbit_density, cutoff, memory):
    bitsets2 = FingerprintsDb(fingerprintsdb).as_dict()
    number_of_bits = bitsets2.number_of_bits
    if query in bitsets2:
        # exact match
        query_bitset = bitsets2[query]
        bitsets1 = {
            query: query_bitset
        }
    else:
        # all bitsets which have a key that starts with query
        bitsets1 = {k: v for k, v in bitsets2.iteritems_startswith(query)}

        if memory:
            # load whole dict in memory so it can be reused for each bitset1
            # deserialization of bitset2 is only done one time
            bitsets2 = {k: v for k, v in bitsets2.iteritems()}

    (corr_st, corr_sto) = corrections(mean_onbit_density)

    distances_iter = distances(bitsets1, bitsets2,
                               number_of_bits, corr_st, corr_sto,
                               cutoff, True)
    sorted_distances = sorted(distances_iter, key=lambda row: row[2], reverse=True)
    dump_pairs_tsv(sorted_distances, out)


def similar_run(query, pairsdbfn, fragmentsdbfn, cutoff, out):
    fragments = FragmentsDb(fragmentsdbfn)
    id2label = fragments.id2label()
    frag_id = fragments[query]['rowid']
    h5file = tables.open_file(pairsdbfn)
    pairs = h5file.root.pairs

    hits = similar(frag_id, pairs, id2label, cutoff)
    dump_pairs_tsv(hits, out)


def similar(frag_id, pairsdb, id2label, cutoff):
    hits = []

    query = id2label[frag_id]
    precision = float(pairsdb.attrs['score_precision'])
    scutoff = int(cutoff * precision)

    query1 = '(a == {}) & (score >= {})'.format(frag_id, scutoff)
    for row in pairsdb.where(query1):
        score = row[2] / precision
        label = id2label[row[1]]
        hits.append((query, score, label))

    query2 = '(b == {}) & (score >= {})'.format(frag_id, scutoff)
    for row in pairsdb.where(query2):
        score = row[2] / precision
        label = id2label[row[0]]
        hits.append((query, score, label))

    # most similar first
    sorted_hits = sorted(hits, reverse=True)

    return sorted_hits