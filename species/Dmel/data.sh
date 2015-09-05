#!/usr/bin/env bash
set -eo pipefail

# Contributed 2015
# Daniel Standage <daniel.standage@gmail.com>

# Configuration
#-------------------------------------------------------------------------------
FULLSPEC="Drosophila melanogaster"
SPEC=Dmel
ORIGFASTA=${SPEC}.orig.fa.gz
ORIGGFF3=dmel-5.48-ncbi.gff3.gz
NCBIBASE=ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/RELEASE_5_48

# Procedure
#-------------------------------------------------------------------------------
source src/data-cli.sh
refrfasta=${WD}/${ORIGFASTA}
refrgff3=${WD}/${ORIGGFF3}
fasta=${WD}/${SPEC}.gdna.fa
gff3=${WD}/${SPEC}.gff3
protfa=${WD}/${SPEC}.all.prot.fa

if [ "$DODOWNLOAD" != "0" ]; then
  echo "[HymHub: $FULLSPEC] download genome and annotations from NCBI"
  for chr in CHR_X/NC_004354 /CHR_2/NT_033778 CHR_2/NT_033779 CHR_3/NT_033777 \
             CHR_3/NT_037436 CHR_4/NC_004353
  do
    basename=$(basename $chr)
    curl ${NCBIBASE}/${chr}.fna \
        > ${WD}/${basename}.fa  \
        2> ${WD}/${basename}.fa.log
    curl ${NCBIBASE}/${chr}.faa \
        > ${WD}/${basename}.prot.faa \
        2> ${WD}/${basename}.prot.log
    curl ${NCBIBASE}/${chr}.gff \
        > ${WD}/${basename}.gff \
        2> ${WD}/${basename}.gff.log
  done
  cat ${WD}/N*_*.fa | gzip -c > $refrfasta
  cat ${WD}/*.prot.faa | gzip -c > ${WD}/protein.fa.gz
  gt gff3 -sort -tidy ${WD}/N*_*.gff 2> ${refrgff3}.log | gzip -c > $refrgff3
fi

if [ "$DOFORMAT" != "0" ]; then
  echo "[HymHub: $FULLSPEC] simplify genome Fasta deflines"
  gunzip -c $refrfasta \
      | perl -ne 's/gi\|\d+\|(ref|gb)\|([^\|]+)\S+/$2/; print' \
      > $fasta

  echo "[HymHub: $FULLSPEC] simplify protein Fasta deflines"
  gunzip -c ${WD}/protein.fa.gz \
      | perl -ne 's/gi\|\d+\|(ref|gb)\|([^\|]+)\S+/$2/; print' \
      > $protfa

  echo "[HymHub: $FULLSPEC] clean up annotation"
  gunzip -c $refrgff3 \
      | grep -v -f species/Dmel/excludes.txt \
      | python species/Dmel/fix-trna.py \
      | tidygff3 2> ${gff3}.tidy.log \
      | python scripts/gff3-format.py - \
      | gt gff3 -retainids -sort -tidy -o ${gff3} -force 2>&1 \
      | grep -v 'has not been previously introduced' \
      | grep -v 'does not begin with "##gff-version"' || true

  echo "[HymHub: $FULLSPEC] verify data files"
  shasum -c species/${SPEC}/checksums.sha
fi

if [ "$DODATATYPES" != "0" ]; then
  source src/datatypes.sh
  get_datatypes $SPEC
fi

if [ "$DOSTATS" != "0" ]; then
  source src/stats.sh
  get_stats $SPEC
fi

if [ "$DOCLEANUP" != "0" ]; then
  source src/cleanup.sh
  data_cleanup
fi

echo "[HymHub: $FULLSPEC] complete!"
