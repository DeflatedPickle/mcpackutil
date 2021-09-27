#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import repackage

repackage.up()

from pathlib import Path
from zipfile import ZipFile

import click as click

from mcpackutil import dotminecraft, extractor, is_pack

author = "deflatedpickle"
name = "mcpackutil"

v_major = "1"
v_min = "0"
v_patch = "3"


def _fversion():
    return f"{v_major}.{v_min}.{v_patch}"


@click.group(name, invoke_without_command=True, context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-v", "--version", "v", is_flag=True)
@click.option("-n", "--name", "n", is_flag=True)
@click.option("-a", "--author", "a", is_flag=True)
@click.option("-d", "--debug", "d", is_flag=True)
@click.pass_context
def main(ctx, v, n, a, d):
    ctx.obj = {
        "d": d
    }

    if v:
        print(_fversion())

    if n:
        print(name)

    if a:
        print(author)


@main.command()
@click.option("-i", "--input", "i", type=click.Path(exists=True))
def valid(i):
    """Validate if a folder or .zip is a resource pack"""
    click.echo(is_pack.is_pack(i))


@main.command()
# https://help.minecraft.net/hc/en-us/articles/360035131551-Where-are-Minecraft-Files-Stored-
def locate():
    """Locate your .minecraft folder"""
    mc = dotminecraft.where()

    if mc.exists():
        print(mc)
    else:
        print(".minecraft not found")


@main.command("zip")
@click.option("-i", "--input", "i", type=click.File("r"))
@click.option("-o", "--output", "o", type=click.File("w"))
def zipup(i, o):
    """Zip up a pack folder"""
    # Credit: https://stackoverflow.com/a/43141399
    src = Path(i).expanduser().resolve(strict=True)

    with ZipFile(o, 'w') as zf:
        for file in src.rglob('*'):
            zf.write(file, file.relative_to(src.parent))


@main.group()
@click.option("-n", "--name", "n", type=str, default="", show_default=True)
@click.option(
    "-v", "--version", "v", type=str,
    help=",".join(dotminecraft.get_vanilla_packs())
)
@click.option("-o", "--output", "o", type=click.Path())
@click.option("-i", "--icons", "i", is_flag=True)
@click.pass_context
def extract(ctx, n, v, o, i):
    """Extract a resource pack from a local Minecraft version"""

    if v is None:
        v = max(dotminecraft.get_vanilla_release())

    if o is None:
        o = "~/Documents"

    ctx.obj = {
        "d": ctx.obj["d"],
        "n": n,
        "v": v,
        "o": o
    }

    if i:
        extractor.asset(
            ctx.obj["v"],
            ctx.obj["o"],
            lambda s: print(s) if ctx.obj["d"] else '',
            ctx.obj["n"],
            "icons"
        )


@extract.command()
@click.argument("f", nargs=-1)
@click.pass_context
def version(ctx, f):
    """Extract the assets of a local Minecraft version"""
    extractor.pack(
        ctx.obj["v"],
        ctx.obj["o"],
        lambda s: print(s) if ctx.obj["d"] else '',
        f,
        ctx.obj["n"]
    )


@extract.group()
@click.pass_context
def asset(ctx):
    """Extract icons, sound and lang files from a local Minecraft client"""
    # Stub
    pass


@asset.command()
@click.option("-i", "--icons", "i", is_flag=True)
@click.option("-l", "--lang", "l", is_flag=True)
@click.option("-s", "--sounds", "s", is_flag=True)
@click.pass_context
def minecraft(ctx, i, l, s):
    """Extracts local core assets associated with Minecraft"""
    p = "minecraft"
    r = []

    if i or not l and not s:
        r.append(f"{p}/icons")

    if l or not i and not s:
        r.append(f"{p}/lang")

    if s or not i and not l:
        r.append(f"{p}/sounds")

    extractor.asset(
        ctx.obj["v"],
        ctx.obj["o"],
        lambda s: print(s) if ctx.obj["d"] else '',
        ctx.obj["n"],
        *r
    )


@asset.command()
@click.option("-l", "--lang", "l", is_flag=True)
@click.option("-t", "--textures", "t", is_flag=True)
@click.pass_context
def realms(ctx, l, t):
    """Extracts local assets associated with Realms"""
    p = "realms"
    r = []

    if l or not t:
        r.append(f"{p}/lang")

    if t or not l:
        r.append(f"{p}/textures")

    extractor.asset(
        ctx.obj["v"],
        ctx.obj["o"],
        lambda s: print(s) if ctx.obj["d"] else '',
        ctx.obj["n"],
        *r
    )


if __name__ == "__main__":
    main()
