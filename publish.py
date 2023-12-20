import asyncio

from argparse import ArgumentParser

from etoile.publisher import TrafficPublisher


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Publish traffic updates to an Ensign topic."
    )
    parser.add_argument(
        "-t",
        "--topic",
        default="figure-updates-json",
        help="Ensign topic to publish to",
    )
    parser.add_argument(
        "-c",
        "--cred-path",
        default="",
        help="Path to Ensign credentials",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--src",
        default="",
        help="Video source",
        required=True,
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show video stream",
    )

    publisher = TrafficPublisher(**vars(parser.parse_args()))
    asyncio.run(publisher.run())