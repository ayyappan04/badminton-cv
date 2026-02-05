import sys
import os
import logging

sys.path.append(os.path.join(os.getcwd(), 'src'))

from rag import KnowledgeBase, ReportGenerator
from utils import setup_logger

logger = setup_logger("verify_rag")

def verify_rag():
    logger.info("Starting RAG verification...")
    
    # 1. Setup Knowledge Base
    kb = KnowledgeBase()
    
    # Add some sample content
    sample_content = [
        ("To improve smash power, focus on wrist snap and full arm rotation.", {"topic": "smash"}),
        ("Good footwork involves split steps and staying on toes.", {"topic": "footwork"}),
        ("The clear shot should be hit high and deep to the back court.", {"topic": "clear"})
    ]
    
    logger.info("Adding documents to Knowledge Base...")
    for text, meta in sample_content:
        kb.add_document(text, meta)
        
    # 2. Setup Report Generator
    generator = ReportGenerator(kb)
    
    # 3. Simulate Metrics
    dummy_metrics = {
        'shuttle_max_speed_kmh': 120.0, # Slow smash
        'players': {
            0: {'total_distance_m': 400.0} # Low distance
        }
    }
    
    # 4. Generate Report
    logger.info("Generating report...")
    report = generator.generate_report(dummy_metrics, [])
    
    logger.info("\n" + "="*40 + "\n" + report + "\n" + "="*40)
    
    if "[MOCK LLM REPORT]" in report:
        logger.info("SUCCESS: Report generated successfully (Mock).")
    else:
        logger.error("FAILURE: Report generation failed.")

if __name__ == "__main__":
    verify_rag()
