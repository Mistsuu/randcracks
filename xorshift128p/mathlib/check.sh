#!/bin/bash

function err() { echo "[!] $@" 1>&2; exit -1; }
function info() { echo "[i] $@" 1>&2; }

ISD_DIR="$CUR_DIR/CU_BJMM"

if [[ "$CUR_DIR" == "" ]]; then
  err CUR_DIR is not set. Exiting...
fi

if [ ! -d "$ISD_DIR" ]; then
  cd "$CUR_DIR"
  ./install.sh
fi

