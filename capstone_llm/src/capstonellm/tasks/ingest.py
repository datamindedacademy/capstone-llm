import argparse
import logging
logger = logging.getLogger(__name__)

def ingest(tag: str):
    pass



def main():
    parser = argparse.ArgumentParser(description="stackoverflow ingest")
    parser.add_argument(
        "-t", "--tag", dest="tag", help="Tag of the question in stackoverflow to process",
        default="python-polars", required=False
    )
    args = parser.parse_args()
    logger.info("Starting the ingest job")

    ingest(args.tag)


if __name__ == "__main__":
    main()
