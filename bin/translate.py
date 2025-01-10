#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT

import copy
import functools
import json
import os
import sys
import unidecode

from boltons import iterutils

if sys.stderr.isatty():
    WRIT = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
else:
    WRIT = ""
    FAIL = ""
    ENDC = ""

last_msg = ""


def print_once(msg, *args, **kwargs):
    global last_msg
    if last_msg == msg:
        return
    print(msg, *args, **kwargs)
    last_msg = msg


def translate_key(path, key, value, filepath):
    cexoloc = value["value"]

    # No translations exist, usually because they're not need (uts, etc.)
    if len(cexoloc) == 0:
        return value

    keys = set(cexoloc.keys())
    strref = cexoloc.get("id")

    # All translations exist
    if (strref and len(keys) == 7) or (len(keys) == 6):
        return value

    path = ".".join([str(x) for x in path]) + "." + key

    # Without a strref, we can't translate using the tlk
    # For some (static placeables), it's only a problem if the placeable is set to non-static
    # or if the item is a creature hide.
    # For others (sounds), it's ignorable
    if not strref:
        print_once(f'{FAIL}warning: no translations available for {path} for file "{filepath}"{ENDC}', file=sys.stderr)
        return value

    # Verify that English translation is the same as the one in English TLK
    translations = get_translations()
    if "0" in keys and cexoloc["0"] != translations["en"][strref]:
        msg = f'{FAIL}warning: translation for {path}, strref {strref} is not the same than value of strref for file "{filepath}"{ENDC}'
        print_once(msg, file=sys.stderr)
        return value

    assert cexoloc.get("0") != ""

    if strref not in translations["fr"]:
        msg = f'{FAIL}warning: translation for {path}, strref {strref} is missing from TLK files for file "{filepath}"{ENDC}'
        print_once(msg, file=sys.stderr)
        return value
        
    cexoloc["2"] = translations["fr"][strref]
    cexoloc["4"] = translations["de"][strref]
    cexoloc["6"] = translations["it"][strref]
    cexoloc["8"] = translations["es"][strref]
    cexoloc["10"] = unidecode.unidecode(translations["pl"][strref])
    return value


def visit(path, key, value, filepath):
    if not isinstance(value, dict):
        return iterutils.default_visit(path, key, value)
    if "type" not in value:
        return iterutils.default_visit(path, key, value)
    if value["type"] != "cexolocstring":
        return iterutils.default_visit(path, key, value)

    value = translate_key(path, key, value, filepath)
    return key, value


def translate_file(filepath):
    print(f'info: translating "{filepath}"...')
    with open(filepath, mode="r", encoding="UTF-8") as fd:
        data = json.loads(fd.read())

    if "__data_type" not in data:
        print(f'warning: skipping "{filepath}" (no header "__data_type")...', file=sys.stderr)
        return

    def _visit(p, k, v):
        return visit(p, k, v, filepath)

    src_data = copy.deepcopy(data)
    data = iterutils.remap(src_data, visit=_visit)
    if data != src_data:
        print(f'{WRIT}info: writing "{filepath}"{ENDC}')
        with open(filepath, mode="w", encoding="UTF-8") as fd:
            data = fd.write(json.dumps(data, indent=2))


def get_files():
    retval = []
    for root, dirnames, files in os.walk("."):
        # To edit dirnames inplace, calculate what we want to keep, then
        # add it to the empty list
        explore = [x for x in dirnames if x.startswith("ut") or x == "dlg"]
        dirnames.clear()
        dirnames += explore

        retval += [f"{root}/{x}" for x in files if x.endswith(".json")]
    return sorted(retval)


@functools.cache
def get_translations():
    print("info: reading TLK files...", file=sys.stderr)
    retval = {}
    for lang in ["en", "es", "fr", "it", "pl", "de"]:
        with open(f"tlk/dialog_{lang}.tlk.json", encoding="UTF-8", mode="r") as fd:
            data = json.loads(fd.read())
            retval[lang] = {x["id"]: x["text"] for x in data["entries"]}
    return retval


def main():
    _ = get_translations()
    files = get_files()
    for file in files:
        translate_file(file)


if __name__ == "__main__":
    main()
