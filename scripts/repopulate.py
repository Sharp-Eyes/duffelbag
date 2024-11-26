"""Script to repopulate all static databases."""

import argparse
import asyncio

import database


async def _main() -> None:
    parser = argparse.ArgumentParser(
        prog="repopulate",
        description="Repopulate the Duffelbag database.",
    )
    parser.add_argument("-i", "--items", action="store_true")
    parser.add_argument("-t", "--tags", action="store_true")
    parser.add_argument("-s", "--skills", action="store_true")
    parser.add_argument("-c", "--characters", action="store_true")

    args = parser.parse_args()

    if not (args.items or args.tags or args.skills or args.characters):
        args.items = args.tags = args.skills = args.characters = True

    if args.items:
        print("Repopulating items...")
        await database.populate_items(clean=True)

    if args.tags:
        print("Repopulating tags...")
        await database.populate_tags(clean=True)

    if args.skills:
        print("Repopulating skills...")
        await database.populate_skills(clean=True)

    if args.characters:
        print("Repopulating characters...")
        await database.populate_characters(clean=True)


def _sync_main() -> None:
    # NOTE: This is the actual Poetry entrypoint.
    asyncio.run(_main())


if __name__ == "__main__":
    _sync_main()
