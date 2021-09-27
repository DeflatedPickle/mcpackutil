#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import shutil
from zipfile import ZipFile

from mcpackutil import dotminecraft
from mcpackutil.is_pack import is_pack


def pack(version: str, output: str, func, folders: list[str], alt: str = ""):
    """Extracts a Minecraft resource pack from your .minecraft"""
    mc = f"{dotminecraft.versions}/{version}/{version}.jar"

    if version is not None and is_pack(mc):
        with ZipFile(mc) as zf:
            expanded = os.path.expanduser(os.path.expandvars(output))

            for file in zf.namelist():
                if file.startswith("assets/minecraft"):
                    if folders and not file.startswith(tuple(folders)):
                        continue
                    else:
                        zf.extract(file, f"{expanded}/{version if alt == '' else alt}")
                        func(f"{version}/{file}")


def asset(version: str, output: str, func, alt: str = "", *resource: str):
    expanded = os.path.expanduser(os.path.expandvars(output))

    ver = -1

    with open(dotminecraft.versions / version / f"{version}.json") as f:
        ver = json.load(f)["assetIndex"]["id"]

    index_obj = {}

    with open(dotminecraft.assets_indexes / f"{ver}.json") as f:
        index_obj = json.load(f)["objects"]

    for k, v in index_obj.items():
        hashish = v["hash"]

        for rt in resource:
            if k.startswith(rt):
                source = dotminecraft.assets_objects / hashish[0:2] / hashish
                destination = f"{expanded}/{version if alt == '' else alt}/assets/{k}"

                try:
                    os.makedirs("/".join(destination.split("/")[:-1]))
                except FileExistsError:
                    pass

                shutil.copy2(source, destination)
                func(f"{version}/assets/{k}")

