#!/usr/bin/env python3
"""
BBC News AI Podcast Transformer - Main Pipeline

Tự động chuyển tin tức BBC thành podcast hàng ngày.
"""

import sys
import argparse
from datetime import datetime
import logging

from src.utils import setup_logging, ensure_directories, create_latest_symlink
import config

# Import modules
from src.data_ingestion import DataIngestion, fetch_articles as fetch_articles_func
from src.script_generator import ScriptGenerator, generate_script as generate_script_func
from src.tts_converter import TTSConverter, convert_to_speech as convert_to_speech_func
from src.github_uploader import GitHubUploader, upload_podcast as upload_podcast_func


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='BBC News AI Podcast Transformer - Tự động tạo podcast từ tin tức BBC'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Chạy mà không upload lên GitHub (dùng để test)'
    )
    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Ngày chạy (YYYY-MM-DD), mặc định là hôm nay'
    )
    parser.add_argument(
        '--skip-ingestion',
        action='store_true',
        help='Bỏ qua bước data ingestion (dùng để test từ bước khác)'
    )
    parser.add_argument(
        '--skip-script',
        action='store_true',
        help='Bỏ qua bước script generation'
    )
    parser.add_argument(
        '--skip-tts',
        action='store_true',
        help='Bỏ qua bước TTS conversion'
    )
    parser.add_argument(
        '--skip-upload',
        action='store_true',
        help='Bỏ qua bước GitHub upload'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Log chi tiết (debug level)'
    )
    return parser.parse_args()


def validate_environment():
    """Validate environment and configuration"""
    logger = logging.getLogger(__name__)

    # Check directories
    dirs = [config.DATA_DIR, config.ARTICLES_DIR, config.PROCESSED_DIR, config.OUTPUT_DIR, config.LOGS_DIR]
    ensure_directories(dirs)

    # Validate config
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)


def run_pipeline(args):
    """Run the full pipeline"""
    logger = logging.getLogger(__name__)
    date_str = args.date or datetime.now().strftime(config.DATE_FORMAT)

    logger.info("=" * 60)
    logger.info(f"BBC News AI Podcast Transformer - Starting pipeline")
    logger.info(f"Date: {date_str}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("=" * 60)

    articles = None
    script = None
    mp3_path = None

    try:
        # STEP 1: Data Ingestion
        if not args.skip_ingestion:
            logger.info("\n" + "=" * 40)
            logger.info("STEP 1: Data Ingestion")
            logger.info("=" * 40)

            ingestion = DataIngestion()
            articles = ingestion.fetch_articles()

            if not articles:
                logger.error("No articles fetched. Cannot continue.")
                return False

            logger.info(f"✓ Fetched {len(articles)} articles")
        else:
            logger.info("Skipping data ingestion (--skip-ingestion flag)")
            # Try to load existing articles
            articles_file = f"{config.ARTICLES_DIR}/articles_{date_str}.json"
            if os.path.exists(articles_file):
                import json
                with open(articles_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                logger.info(f"Loaded {len(articles)} articles from {articles_file}")
            else:
                logger.error(f"No articles file found: {articles_file}")
                return False

        # STEP 2: Script Generation
        if not args.skip_script:
            logger.info("\n" + "=" * 40)
            logger.info("STEP 2: Script Generation")
            logger.info("=" * 40)

            generator = ScriptGenerator()
            script = generator.generate_script(articles)

            script_file = f"{config.PROCESSED_DIR}/script_{date_str}.md"
            logger.info(f"✓ Script generated: {script_file}")
        else:
            logger.info("Skipping script generation (--skip-script flag)")
            # Try to load existing script
            script_file = f"{config.PROCESSED_DIR}/script_{date_str}.md"
            if os.path.exists(script_file):
                with open(script_file, 'r', encoding='utf-8') as f:
                    script = f.read()
                logger.info(f"Loaded script from {script_file}")
            else:
                logger.error(f"No script file found: {script_file}")
                return False

        # STEP 3: TTS Conversion
        if not args.skip_tts:
            logger.info("\n" + "=" * 40)
            logger.info("STEP 3: Text-to-Speech Conversion")
            logger.info("=" * 40)

            converter = TTSConverter()
            mp3_path = converter.convert_to_speech(script)

            logger.info(f"✓ MP3 generated: {mp3_path}")
        else:
            logger.info("Skipping TTS conversion (--skip-tts flag)")
            mp3_path = f"{config.OUTPUT_DIR}/podcast_{date_str}.mp3"
            if not os.path.exists(mp3_path):
                logger.error(f"No MP3 file found: {mp3_path}")
                return False
            logger.info(f"Using existing MP3: {mp3_path}")

        # STEP 4: GitHub Upload
        if not args.dry_run and not args.skip_upload:
            logger.info("\n" + "=" * 40)
            logger.info("STEP 4: GitHub Upload")
            logger.info("=" * 40)

            uploader = GitHubUploader()
            public_url = uploader.upload_podcast(mp3_path, date_str)

            if public_url:
                logger.info(f"✓ Podcast published: {public_url}")
            else:
                logger.error("Failed to upload podcast")
                return False

        elif args.dry_run or args.skip_upload:
            logger.info("\n" + "=" * 40)
            logger.info("STEP 4: Skipped (dry run or --skip-upload)")
            logger.info("=" * 40)
            logger.info(f"MP3 file: {mp3_path}")
            logger.info("To upload, run without --dry-run flag")

        # Create latest symlink/copy
        if mp3_path:
            latest_path = f"{config.OUTPUT_DIR}/podcast_latest.mp3"
            create_latest_symlink(mp3_path, latest_path)

        logger.info("\n" + "=" * 60)
        logger.info("✓ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

        return True

    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        return False

    except Exception as e:
        logger.error(f"\nPipeline failed with error: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    args = parse_arguments()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else config.LOG_LEVEL
    logger = setup_logging(config.LOGS_DIR, log_level)

    # Validate environment
    validate_environment()

    # Run pipeline
    success = run_pipeline(args)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()