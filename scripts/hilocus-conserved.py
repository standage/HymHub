#!/usr/bin/env python
#
# HymHub is distributed under the CC BY 4.0 License. See the
# 'LICENSE' file in the HymHub code distribution or online at
# https://github.com/BrendelGroup/HymHub/blob/master/LICENSE.

import random
import sys
import hilocus_utils


def ilocus_isoforms(rootdir='.'):
    ilocus2mrna = dict()
    mapping = dict()
    for species in ['Acep', 'Ador', 'Aech', 'Aflo', 'Amel', 'Bimp', 'Bter',
                    'Cflo', 'Dmel', 'Hsal', 'Mrot', 'Nvit', 'Pbar', 'Pdom',
                    'Sinv', 'Tcas']:
        mrnafile = '%s/species/%s/%s.ilocus.mrnas.txt' % (rootdir, species,
                                                          species)
        protfile = '%s/species/%s/%s.protein2ilocus.txt' % (rootdir, species,
                                                            species)
        with open(mrnafile, 'r') as fhm, open(protfile, 'r') as fhp:
            for line in fhm:
                hid, mid = line.rstrip().split()
                ilocus2mrna[hid] = mid
            for line in fhp:
                pid, hid = line.rstrip().split()
                mid = ilocus2mrna[hid]
                mapping[hid] = (mid, pid)

    return mapping


if __name__ == '__main__':
    import argparse
    import sys

    desc = ('Select hiLoci with single-copy orthologs from the main '
            'Hymenopteran lineages: bees, ants, vespid wasps, and parasitic '
            'wasps')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--multiple', action='store_true',
                        help='if all four lineages are represented in a '
                        'hiLocus but not in single copies, choose a '
                        'representative copy rather than discarding the '
                        'hiLocus')
    parser.add_argument('-r', '--rootdir', default='.',
                        help='path to HymHub root directory; default is '
                        'current directory')
    parser.add_argument('hiloci', type=argparse.FileType('r'),
                        default=sys.stdin, help='hiLocus data table')
    args = parser.parse_args()

    ilocus_mapping = ilocus_isoforms(rootdir=args.rootdir)

    print '\t'.join(['hiLocus', 'iLocus', 'Species', 'Lineage', 'Mrna',
                     'Protein'])
    for line in args.hiloci:
        values = line.rstrip().split('\t')
        if values[4] not in ['Hymenoptera', 'Insects']:
            continue
        species = values[6].split(',')
        if 'Pdom' not in species or 'Nvit' not in species:
            continue
        iloci = values[5].split(',')
        hid = values[0]

        ants = hilocus_utils.in_ants(iloci, as_list=True)
        bees = hilocus_utils.in_bees(iloci, as_list=True)
        pdom = hilocus_utils.in_pdom(iloci, as_list=True)
        nvit = hilocus_utils.in_nvit(iloci, as_list=True)
        if None in [ants, bees, pdom, nvit]:
            # Lack representative from one or more clades; moving on
            continue

        for spec, ilocus, lineage in ants + bees + pdom + nvit:
            mrnaid, protid = ilocus_mapping[ilocus]
            print '\t'.join([hid, ilocus, spec, lineage, mrnaid, protid])