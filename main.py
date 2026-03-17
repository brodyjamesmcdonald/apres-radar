"""
Apres Radar - Colorado Resort Event Scraper
Main orchestrator that runs all 12 resort scrapers daily
"""

import os
import sys
from datetime import datetime, timedelta
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from resort_scrapers import (
    EldoraScraper,
    CopperScraper,
    WinterParkScraper,
    SteamboatScraper,
    AspenSnowmassScraper,
    ArapahoeBasinScraper,
    KeystoneScraper,
    BreckenridgeScraper,
    VailScraper,
    CrestedButteScraper,
    BeaverCreekScraper,
    TellurideScraper
)

# Database connection - using session pooler port 6543
DATABASE_URL = os.getenv('DATABASE_URL')

class ScraperOrchestrator:
    """Manages all resort scrapers and saves to PostgreSQL"""
    
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.scrapers = [
            CopperScraper(),
            WinterParkScraper(),
            EldoraScraper(),
            SteamboatScraper(),
            AspenSnowmassScraper(),
            ArapahoeBasinScraper(),
            KeystoneScraper(),
            BreckenridgeScraper(),
            VailScraper(),
            CrestedButteScraper(),
            BeaverCreekScraper(),
            TellurideScraper()
        ]
        self.results = {
            'success': [],
            'failed': [],
            'total_events': 0
        }
    
    def run_all_scrapers(self):
        """Run all resort scrapers"""
        print("\n" + "="*70)
        print(f"🏔️  APRES RADAR - COLORADO EVENT SCRAPER")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MT')}")
        print("="*70 + "\n")
        
        for scraper in self.scrapers:
            try:
                print(f"🔍 Scraping {scraper.resort_name}...")
                events = scraper.scrape()
                
                if events:
                    saved_count = self.save_events(events, scraper.resort_name)
                    self.results['success'].append(scraper.resort_name)
                    self.results['total_events'] += saved_count
                    print(f"   ✅ {scraper.resort_name}: {saved_count} events saved")
                else:
                    print(f"   ⚠️  {scraper.resort_name}: No events found")
                    self.results['failed'].append(f"{scraper.resort_name} (no events)")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                error_msg = f"{scraper.resort_name}: {str(e)}"
                self.results['failed'].append(error_msg)
                print(f"   ❌ {scraper.resort_name}: ERROR - {e}")
                continue
        
        self.print_summary()
        self.cleanup_old_events()
        self.conn.close()
    
    def save_events(self, events: list, resort_name: str) -> int:
        """Save events to PostgreSQL"""
        saved_count = 0
        cursor = self.conn.cursor()
        
        for event in events:
            try:
                # Check if event already exists
                cursor.execute(
                    """
                    SELECT id FROM events 
                    WHERE event_name = %s AND event_date = %s AND resort_name = %s
                    """,
                    (event['event_name'], event['event_date'], resort_name)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing event
                    cursor.execute(
                        """
                        UPDATE events SET
                            description = %s,
                            event_time = %s,
                            venue = %s,
                            url = %s,
                            scraped_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            event.get('description'),
                            event.get('event_time'),
                            event.get('venue'),
                            event.get('url'),
                            existing[0]
                        )
                    )
                else:
                    # Insert new event
                    cursor.execute(
                        """
                        INSERT INTO events (
                            resort_name, event_name, event_date, event_time,
                            description, event_type, venue, url, is_major_event,
                            scraped_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """,
                        (
                            resort_name,
                            event['event_name'],
                            event['event_date'],
                            event.get('event_time'),
                            event.get('description'),
                            event.get('event_type', 'other'),
                            event.get('venue'),
                            event.get('url'),
                            event.get('is_major_event', False)
                        )
                    )
                
                self.conn.commit()
                saved_count += 1
                
            except Exception as e:
                print(f"      ⚠️  Error saving event '{event.get('event_name')}': {e}")
                self.conn.rollback()
                continue
        
        cursor.close()
        return saved_count
    
    def cleanup_old_events(self):
        """Delete old non-major events (30 days past)"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            cursor.execute(
                """
                DELETE FROM events 
                WHERE event_date < %s AND is_major_event = FALSE
                """,
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            self.conn.commit()
            cursor.close()
            
            print(f"\n🗑️  Cleaned up {deleted_count} old events (>30 days past)")
            
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    def print_summary(self):
        """Print scraping summary"""
        print("\n" + "="*70)
        print("📊 SCRAPING SUMMARY")
        print("="*70)
        print(f"✅ Successful: {len(self.results['success'])} resorts")
        print(f"❌ Failed: {len(self.results['failed'])} resorts")
        print(f"📅 Total Events: {self.results['total_events']}")
        
        if self.results['failed']:
            print("\n⚠️  Failed Resorts:")
            for failure in self.results['failed']:
                print(f"   • {failure}")
        
        print("\n" + "="*70)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MT')}")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL environment variable required")
        sys.exit(1)
    
    orchestrator = ScraperOrchestrator()
    orchestrator.run_all_scrapers()


if __name__ == "__main__":
    main()

