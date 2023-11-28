"""Script to repopulate all static databases."""

import asyncio

import database


async def _main() -> None:
    print("Repopulating items...")
    await database.populate_items(clean=True)

    print("Repopulating tags...")
    await database.populate_tags(clean=True)

    print("Repopulating skills...")
    await database.populate_skills(clean=True)

    print("Repopulating characters...")
    await database.populate_characters(clean=True)


def _sync_main() -> None:
    # NOTE: This is the actual Poetry entrypoint.
    asyncio.run(_main())


if __name__ == "__main__":
    _sync_main()
