import logging

from csv_to_ddl.argument_parser import ArgumentParser
from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.config.config_provider import DefaultConfigProvider
from csv_to_ddl.csv_to_ddl_converter import CSVToDDLConverter
from csv_to_ddl.schema_analysis.models.dialects import DatabaseDialect


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )


def csv_to_ddl():
    parser = ArgumentParser.create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        if not args.input.exists():
            logger.error(f"Input path does not exist: {args.input}")
            return 1

        ConfigManager.initialize(DefaultConfigProvider())
        converter = CSVToDDLConverter(DatabaseDialect(args.dialect))

        results = converter.convert(input_path=args.input)
        converter.write_output(args.output, results)

        return 0

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(csv_to_ddl())
