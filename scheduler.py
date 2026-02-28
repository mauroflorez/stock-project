#!/usr/bin/env python3
"""
Scheduler Script
Runs the analysis automatically on a schedule
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
from config import RUN_TIME, TIMEZONE
import pytz


def run_analysis_job():
    """Run the analysis and report generation, then log output"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*70}")
    print(f"Scheduled Run Started: {timestamp}")
    print(f"{'='*70}\n")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Step 1: Run the main analysis
        print("Step 1/2: Running stock analysis (main.py)...")
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"\n✗ Analysis failed at {timestamp}")
            print(result.stderr)
            return
        
        print(f"\n✓ Analysis completed successfully")
        
        # Step 2: Generate HTML reports
        print("\nStep 2/2: Generating HTML reports (generate_report.py)...")
        result2 = subprocess.run(
            [sys.executable, "generate_report.py"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        print(result2.stdout)
        
        if result2.returncode == 0:
            print(f"\n✓ Reports generated successfully at {timestamp}")
        else:
            print(f"\n✗ Report generation failed at {timestamp}")
            print(result2.stderr)
            
    except Exception as e:
        print(f"\n✗ Error running scheduled job: {str(e)}")


def main():
    """Main scheduler loop"""
    
    print("="*70)
    print("STOCK INVESTMENT PLANNER - SCHEDULER")
    print("="*70)
    print()
    print(f"Configured to run daily at: {RUN_TIME} ({TIMEZONE})")
    print(f"Press Ctrl+C to stop the scheduler")
    print()
    
    # Schedule the job
    schedule.every().day.at(RUN_TIME).do(run_analysis_job)
    
    # Also run immediately on startup
    print("Running initial analysis now...")
    run_analysis_job()
    
    print(f"\n{'='*70}")
    print(f"Scheduler is now running. Next run: {schedule.next_run()}")
    print(f"{'='*70}\n")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")
        print("Goodbye!")


if __name__ == "__main__":
    main()

