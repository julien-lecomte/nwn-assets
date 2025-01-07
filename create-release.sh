#!/usr/bin/env bash

set -eu

export PATH=./bin:"${PATH}"
export PS4=""

(./translate.py 3>&2 2>&1 1>&3) | tee translate.log

tag=$(git for-each-ref refs/tags --sort=-taggerdate --format='%(refname)' --count=1)
tag=${tag##*/}
tag=${1:-$tag}

rm -fr ${tag}/*
mkdir -p ${tag}

for ext in dlg ut*; do
  mkdir -p ${tag}/${ext}
  echo info: Running nwn_gff on ${ext} files...
  for file in $(git status -s --untracked-files=no --ignored=no ${ext} | grep ' M ' | sed 's/ M //'); do
    nwn_gff -i ${file} -o ${tag}/${file%%.json}
  done
done

mkdir -p ${tag}/tlk/
for file in tlk/dialog_*.tlk.csv; do
  (set -x; nwn_tlk -i "${file}" -o ${tag}/${file%%.csv})
done

nwn_erf -c -f nwn_i18n.hak -e hak -r2 ${tag}
