#!python3
 
import argparse
import logging
from . import Engine, test

"""The command line arguments"""
args = None

def main():
    """Perform command line steamback operations"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Show debug log messages",
                        action="store_true")
    parser.add_argument("--test", help="Run integration code test",
                        action="store_true")

    global args
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'Steamback running...')

    e = Engine(logger)
    if args.test:
        test.testAll(e)


if __name__ == "__main__":
    main()
