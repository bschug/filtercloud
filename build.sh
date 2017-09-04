#!/bin/bash

mode=$1

outdir=$HOME/PathOfExile
tpldir=templates
template=$tpldir/main.template
settings=$tpldir/$mode.json
style=$tpldir/style.json
outfile=$outdir/gg-$mode.filter

export PYTHONPATH=$PWD/src
python3 -m run $template $settings $style > $outfile
