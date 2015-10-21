#!/usr/bin/env bash
set -eo pipefail

# Contributed 2015
# Daniel Standage <daniel.standage@gmail.com>

# Configuration
#-------------------------------------------------------------------------------
FULLSPEC="Dinoponera quadriceps"
SPEC=Dqua
MODE="hymbase"

# Procedure
#-------------------------------------------------------------------------------
source src/data-cli.sh
source src/filenames.sh

if [ "$DODOWNLOAD" != "0" ]; then
  echo "[HymHub: $FULLSPEC] download genome assembly"
  seqfile=DQUA.v01.fa.gz
  curl -o ${WD}/${seqfile} http://wasp.crg.eu/${seqfile} 2> ${WD}/${seqfile}.log

  echo "[HymHub: $FULLSPEC] download protein sequences"
  protfile=DQUA.v01.pep.fa
  curl http://wasp.crg.eu/${protfile} 2> ${WD}/${protfile}.log \
      | gzip -c > ${WD}/protein.fa.gz

  echo "[HymHub: $FULLSPEC] downloading genome annotation"
  featfile=DQUA.v01.gff3
  curl -o ${WD}/${featfile} http://wasp.crg.eu/DQUA.v01.gff3 2> ${WD}/${featfile}.log
fi

if [ "$DOFORMAT" != "0" ]; then
  echo "[HymHub: $FULLSPEC] renaming data files"

  cp ${WD}/DQUA.v01.fa.gz ${WD}/Dqua.gdna.fa.gz
  gunzip -f ${WD}/Dqua.gdna.fa.gz
  gunzip -c ${WD}/protein.fa.gz > ${WD}/Dqua.all.prot.fa

  sed 's/transcript/mRNA/' ${WD}/DQUA.v01.gff3 \
      | python scripts/fix-regions.py ${WD}/Dqua.gdna.fa \
      | python scripts/gff3-format.py --mode pcan - \
      | gt gff3 -sort -tidy \
      > ${WD}/Dqua.gff3

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
