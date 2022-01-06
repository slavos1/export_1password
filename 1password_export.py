#!/usr/bin/env python
from pathlib import Path
from subprocess import Popen, STDOUT, PIPE
from logging import getLogger, basicConfig
from os import environ
import json
from operator import itemgetter
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from urllib.parse import urlsplit, urlunsplit
from itertools import chain

import pandas as pd

ONE_PASSWORD_CLI = "op"
GROUPING_DELIMITER = " :: "
MONTHS = """
January
February
March
April
May
June
July
August
September
October
November
December
""".strip().split()

_logger = getLogger()


def op(*args, fail_on_exc=True, quiet=False):
    p = Popen(
        [
            ONE_PASSWORD_CLI,
            *args,
        ],
        stdout=PIPE,
        stderr=PIPE,
        # env=environ,
    )
    o, e = p.communicate()
    if o:
        o = json.loads(o.strip().decode("utf-8"))
    if e:
        error = e.strip().decode()
        if fail_on_exc:
            raise RuntimeError(
                f"[{ONE_PASSWORD_CLI} {args}] exited with error {error!r} and code {p.returncode}"
            )
        if not quiet:
            _logger.error(f'"{error}"')
    return o


def get_vaults():
    return sorted(map(itemgetter("name"), op("list", "vaults")))


def simplify_url(url):
    """Remove params and fragment"""
    scheme, location, path, query, fragment = urlsplit(url)
    return urlunsplit((scheme, location, path, "", ""))


def as_credit_card(_fields):
    fields = dict((f["n"], f["v"]) for f in _fields)
    _i = str(fields["expiry"])
    expiry_year, expiry_month = _i[:4], _i[4:]
    return f"""NoteType:Credit Card
Language:en-US
Name on Card:{fields['cardholder']}
Type:{fields['type'].capitalize()}
Number:{fields['ccnum']}
Security Code:{fields['cvv']}
Start Date:,
Expiration Date:{MONTHS[int(expiry_month) - 1]},{expiry_year}
Notes:"""


def to_csv(args):
    if args.max_count:
        _logger.info(f"Will fetch max {args.max_count} items")
    if args.dumper:
        _logger.info(f"Will dump items to {args.dumper.name} as we fetch them")

    for vault_name in get_vaults():
        grouping = GROUPING_DELIMITER.join([args.grouping, vault_name])
        _logger.info(
            f"Fetching items from {vault_name} vault, will be grouped to {grouping}"
        )
        # Lastpass CSV: url,username,password,totp,extra,name,grouping,fav
        for i, _item in enumerate(
            sorted(
                filter(
                    lambda i: i["trashed"] == "N",
                    op("list", "items", "--vault", vault_name),
                ),
                key=itemgetter("uuid"),
            ),
            1,
        ):
            if args.max_count and i > args.max_count:
                break
            uuid = _item["uuid"]
            if args.include and uuid not in args.include:
                continue
            _logger.info(f"{i:3d}. Fetching item with id {uuid}")
            item = op("get", "item", uuid)
            overview = item["overview"]

            details = item["details"]
            fields = details.get("fields", [])

            def _fields():
                for f in fields:
                    if f["designation"] in ["username", "password"]:
                        yield f["designation"], f["value"]

            secure_note = not overview.get("url")
            if not fields:
                _logger.warning(
                    f"Item with {uuid} does not have details/fields, will export as a Secure Note"
                )
                secure_note = True

            try:

                def _iter_sfields():
                    for s in details.get("sections", []):
                        yield s.get("fields")

                ccard_fields = chain.from_iterable(_iter_sfields())
                note_content = as_credit_card(ccard_fields)
            except:
                note_content = details["notesPlain"]

            d = dict(
                username="",
                password="",
                # XXX if not url, it is a LastPass Secure Note
                url="http://sn" if secure_note else simplify_url(overview["url"]),
                totp="",  # no idea what this is
                extra=note_content,
                name=overview["title"],
                grouping=grouping,
                fav="0",
                _id=uuid,
            )
            d.update(_fields())
            if args.dumper:
                json.dump(d, args.dumper)
                print(file=args.dumper)
                args.dumper.flush()
            yield d


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Show debug logs",
    )
    parser.add_argument(
        "-u",
        "--dumper",
        help="Dump raw items to the file",
        type=FileType("w"),
        metavar="PATH",
    )
    parser.add_argument(
        "-i",
        "--include",
        help="Only show output for this UUID",
        metavar="UUID",
        nargs="+",
    )
    parser.add_argument(
        "-g",
        "--grouping",
        help="Folder to be created in LastPass",
        default="1password_import",
        metavar="STRING",
    )
    parser.add_argument(
        "-n", "--max-count", help="Max item count to fetch", type=int, metavar="INT"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        help="Output file",
        type=Path,
        metavar="PATH",
    )
    args = parser.parse_args()
    basicConfig(
        level="DEBUG" if args.debug else "INFO",
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    _logger.debug(args)
    items = pd.DataFrame(to_csv(args))
    _logger.info(f"Writing {len(items.index)} record(s) to {args.output_file}")
    items.to_csv(args.output_file, index=False)
