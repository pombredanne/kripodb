# Kripo DB

[![Build Status](https://travis-ci.org/3D-e-Chem/kripodb.svg?branch=master)](https://travis-ci.org/3D-e-Chem/kripodb)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/4878758675a0402bb75019672fa6e45c)](https://www.codacy.com/app/NLeSC/kripodb)
[![Codacy Badge](https://api.codacy.com/project/badge/coverage/4878758675a0402bb75019672fa6e45c)](https://www.codacy.com/app/NLeSC/kripodb)
[![DOI](https://zenodo.org/badge/19641/3D-e-Chem/kripodb.svg)](https://zenodo.org/badge/latestdoi/19641/3D-e-Chem/kripodb)
[![Docker Hub](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/3dechem/kripodb/)

Library to interact with Kripo fragment, fingerprint and similarity data files.

KRIPO stands for Key Representation of Interaction in POckets, see [reference](http://dx.doi.org/10.1186/1758-2946-6-S1-O26) for more information.

# Install

Requirements:

* rdkit, http://rdkit.org, to read SDF files and generate smile strings from molecules
* libhdf5 headers, to read/write distance matrix in hdf5 format

```
pip install -U setuptools
pip install numpy
python setup.py install
```

# Usage

To see available commands
```
kripodb --help
```

## Create all

Commands to create all data files
```
kripodb fragments shelve fragments.shelve fragments.sqlite
kripodb fragments sdf fragment??.sdf fragments.sqlite
kripodb fragments pdb fragments.sqlite
kripodb fingerprints import 01.fp 01.fp.db
kripodb fingerprints import 02.fp 02.fp.db
kripodb fingerprints distances --fragmentsdbfn fragments.sqlite 01.fp.db 01.fp.db dist_01_01.h5
kripodb fingerprints distances --fragmentsdbfn fragments.sqlite 01.fp.db 02.fp.db dist_01_02.h5
kripodb fingerprints distances --fragmentsdbfn fragments.sqlite 02.fp.db 01.fp.db dist_02_01.h5
kripodb fingerprints distances --fragmentsdbfn fragments.sqlite 02.fp.db 02.fp.db dist_02_02.h5
kripodb distances merge dist_*_*.h5  dist_all.h5
kripodb distances optimize dist_all.h5
kripodb distances serve dist_all.h5
```

## Search for most similar fragments

Command to find fragments most similar to `3kxm_K74_frag1` fragment.
```
kripodb similar dist_all.h5 3kxm_K74_frag1 --cutoff 0.45
```

# Data

An example data set included in the [data/](data/) directory. See [data/README.md](data/README.md) for more information.

# Knime

The [Knime-KripoDB-example.zip](https://github.com/3D-e-Chem/knime-kripodb/blob/master/examples/Knime-KripoDB-example.zip) file is an example workflow showing how to use KripoDB python package inside Knime (http://www.knime.org).
It can be run by importing it into Knime.
Make sure the Python used by Knime is the same the Python with kripodb package installed.

The https://github.com/3D-e-Chem/knime-kripodb repo adds KripoDB code templates to Knime.

# Development of KripoDB

Install the development deps with:
```
pip install -r requirements.txt
```

# Docker

## Create image

```
docker build -t 3dechem/kripodb .
```

## Run container

Show the kripodb help with
```
docker run --rm 3dechem/kripodb kripodb --help
```

To calculate the mean bit density of the fingerprints in the `fingerprints.sqlite` file in the current working directory use following command.
```
docker run --rm -u $UID -v $PWD:/data 3dechem/kripodb kripodb meanbitdensity /data/fingerprints.sqlite
```

# Web service

The Kripo data files can be queried using a web service.

Start webservice with:
```
kripodb serve --port 8084 data/distances.h5
```
It will print the urls for the swagger spec and UI.

Note! The webservice returns a limited amount of results. To get all results use local files.

# Reference

KRIPO – a structure-based pharmacophores approach explains polypharmacological effects;
Tina Ritschel, Tom JJ Schirris, and Frans GM Russel; J Cheminform. 2014; 6(Suppl 1): O26;
Published online 2014 Mar 11; http://dx.doi.org/10.1186/1758-2946-6-S1-O26
