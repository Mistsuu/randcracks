#!/bin/bash

function err() { echo "[!] $@" 1>&2; exit -1; }
function info() { echo "[i] $@" 1>&2; }

ISD_DIR="$CUR_DIR/CU_BJMM"
PATCH_FILE="$CUR_DIR/patch.diff"
ISD_GIT_URL="https://github.com/sh-narisada/CU_BJMM"

if [[ "$CUR_DIR" == "" ]]; then
  err CUR_DIR is not set. Exiting...
fi

for cmd in "git" "nvcc" "gcc" "g++" "patch" "make"; do
  which "$cmd" 1>/dev/null
  if [[ "$?" -ne 0 ]]; then
    err "$cmd" not found, required by the installer.
  fi
done

if [[ ! -e "$PATCH_FILE" ]]; then
  err "Cannot find patch file at $PATCH_FILE to patch the library!"
fi

if [ ! -e "$ISD_DIR" ]; then
  git clone "$ISD_GIT_URL" || err Clone repository at $ISD_GIT_URL failed. Exiting...
fi

cd "$ISD_DIR"
patch -p0 < "$PATCH_FILE"

if [ ! -d cuBJMM+ ]; then
  err The author must have updated the repository...
fi

cd cuBJMM+
make || err Error making CUBJMM library.

exit 0

