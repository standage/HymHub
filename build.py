#!/usr/bin/env python
#
# Copyright (c) 2015, Daniel S. Standage and CONTRIBUTORS
#
# HymHub is distributed under the CC BY 4.0 License. See the
# 'LICENSE' file in the HymHub code distribution or online at
# https://github.com/BrendelGroup/HymHub/blob/master/LICENSE.

import argparse
import sys
import yaml
import ncbi
import pdom

def get_args():
    """Parse command-line arguments."""
    desc = 'Execute the main HymHub build process'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-r', '--root', metavar='DIR', default='.',
                        help='HymHub root directory; default is current dir')
    parser.add_argument('--species', metavar='LIST', default=None,
                        help='comma-separated list of species labels to '
                        'process (such as "Amel,Hsal,Nvit,Pdom"); default is '
                        'to process all')
    parser.add_argument('-p', '--num_procs', metavar='N', default=1, type=int,
                        help='number of processors available for local tasks; '
                        'default is 1')
    parser.add_argument('-l', '--logfile', metavar='LOG', default=sys.stderr,
                        type=argparse.FileType('w'),
                        help='log file; default is terminal (stderr)')
    tasks = parser.add_argument_group('build tasks')
    tasks.add_argument('-d', '--download', action='store_true',
                       help='download data from remote servers')
    tasks.add_argument('-f', '--format', action='store_true',
                       help='polish raw primary data files')
    tasks.add_argument('-t', '--types', action='store_true',
                       help='extract data for various genomic feature types')
    tasks.add_argument('-s', '--stats', action='store_true',
                       help='compute statistics for each data type')
    tasks.add_argument('-c', '--cleanup', action='store_true',
                       help='clean up intermediate data files')
    return parser.parse_args()


def load_configs(species_list, rootdir='.'):
    """
    Load configuration files for each species.
    """
    configs = dict()
    for species in species_list:
        configfile = '%s/species/%s/data.yml' % (rootdir, species)
        with open(configfile, 'r') as cfg:
            configs[species] = yaml.load(cfg)
    return configs


def download_task(config, rootdir='.', logstream=sys.stderr):
    """
    Run the download task of the build procedure.

    Genome sequence, genome annotations, and protein sequences must be
    downloaded for every species. The download procedure depends on the source
    of the data.
    """
    source = config['source']
    assert source in ['ncbi', 'ncbi_flybase', 'custom']

    if source == 'ncbi':
        gdnatype = config['genomeseq']['type']
        if gdnatype == 'scaffolds':
            dnafunc = ncbi.download_scaffolds
        elif gdnatype == 'chromosomes':
            dnafunc = ncbi.download_chromosomes
        dnafunc(config, rootdir=rootdir, logstream=logstream)
        ncbi.download_annotation(config, rootdir=rootdir, logstream=logstream)
        ncbi.download_proteins(config, rootdir=rootdir, logstream=logstream)

    elif source == 'ncbi_flybase':
        ncbi.download_flybase(config, rootdir=rootdir, logstream=logstream)

    elif source == 'custom':
        handler = config['download_handler']
        # Add to this list if more custom handlers are needed
        assert handler in ['download_pdom']
        if handler == 'download_pdom':
            pdom.download(config, rootdir=rootdir, logstream=logstream)


def main(args):
    """Main build procedure."""
    if not args.download and not args.format and not args.types and \
            not args.stats and not args.cleanup:
        print >> sys.stderr, 'please specify build task(s)'
        sys.exit(1)

    if args.num_procs != 1:
        print >> sys.stderr, 'warning: parallel processing not yet supported'

    if args.species == None:
        args.species = ('Acep,Ador,Aech,Aflo,Amel,Bimp,Bter,Cflo,Dmel,Hsal,'
                        'Mrot,Nvit,Pbar,Pdom,Sinv,Tcas')
    args.species_list = args.species.split(',')
    configs = load_configs(args.species_list, args.root)

    if args.download:
        for species in args.species_list:
            download_task(configs[species], rootdir=args.root,
                          logstream=args.logfile)

    for species in args.species_list:
        pass


if __name__ == '__main__':
    main(get_args())