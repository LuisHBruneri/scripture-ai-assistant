import sys
import os
import logging

# Add the project root to python path to allow imports from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.data_ingestion.enrich_knowledge import main as run_enrichment
from backend.data_ingestion.ingest import ingest_data
from backend.data_ingestion.download_bible import download_and_convert as download_bible

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TRAINER")

def main():
    logger.info("==================================================")
    logger.info("   STARTING FULL AGENT TRAINING (ENRICH + INGEST) ")
    logger.info("==================================================")

    # Step 0: Ensure Bible Data Exists
    logger.info("\n>>> STEP 0: CHECKING BIBLE DATA...")
    try:
        if not os.path.exists("source_docs/bible_data.json"):
            logger.info("bible_data.json not found. Downloading...")
            download_bible()
        else:
            logger.info("bible_data.json already exists. Skipping download.")
    except Exception as e:
        logger.error(f"❌ Bible download failed: {e}")
        # Proceeding might be dangerous if bible is missing, but let's try
        
    # Step 1: Enrich Knowledge Base
    logger.info("\n>>> STEP 1: ENRICHING KNOWLEDGE BASE (Downloading Resources)...")
    try:
        run_enrichment()
        logger.info("✅ Enrichment completed successfully.")
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        # We might continue if it's just a network error on one file, 
        # but let's assume we want to proceed to ingest whatever we have.

    # Step 2: Intelligent Ingestion
    logger.info("\n>>> STEP 2: RUNNING INTELLIGENT INGESTION (Building Vector DB)...")
    try:
        ingest_data()
        logger.info("✅ Ingestion completed successfully.")
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

    logger.info("\n")
    logger.info("==================================================")
    logger.info("   🎉 AGENT TRAINING COMPLETE! READY TO SERVE.    ")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
