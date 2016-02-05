# Example data set

* fragments.sqlite - Fragments sqlite database containing a small number of fragments with their smiles string and molblock.
* fingerprints.sqlite - Fingerprints sqlite database with fingerprint stored as [fastdumped intbitset](http://intbitset.readthedocs.org/en/latest/index.html#intbitset.intbitset.fastdump)
* distances.h5 - HDF5 file with distance matrix of fingerprints using modified tanimoto coefficient 

## Creating tiny data set

1. Create fingerprints db with 1000 fingerprints
```
head -1001 fingerprint01.fp.gz | kripodb makebits2fingerprintsdb - fingerprints.sqlite
```

2. Shrink fragments db to only contain fragments which have a fingerprint
```
cat | sqlite3 fragments.sqlite <<EOF
ATTACH DATABASE 'fingerprints.sqlite' AS fp;
DELETE FROM molecules WHERE frag_id NOT IN (SELECT frag_id FROM fp.bitsets);
DELETE FROM fragments WHERE frag_id NOT IN (SELECT frag_id FROM fp.bitsets);
VACUUM;
EOF

```

3. Create distance matrix

```
kripodb pairs --fragmentsdbfn fragments.sqlite fingerprints.sqlite fingerprints.sqlite distances.h5
```