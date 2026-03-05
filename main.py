"""
Apres Radar - Colorado Resort Event Scraper
Main orchestrator that runs all 12 resort scrapers daily
"""

import os
import sys
from datetime import datetime, timedelta
import time
from supabase import create_client, Client
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

# Supabase connection
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

class ScraperOrchestrator:
    """Manages all resort scrapers and saves to Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.scrapers = [
            EldoraScraper(),
            CopperScraper(),
            WinterParkScraper(),
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
    
    def save_events(self, events: list, resort_name: str) -> int:
        """Save events to Supabase"""
        saved_count = 0
        
        for event in events:
            try:
                # Check if event already exists (avoid duplicates)
                existing = self.supabase.table('events').select('id').eq(
                    'event_name', event['event_name']
                ).eq('event_date', event['event_date']).eq(
                    'resort_name', resort_name
                ).execute()
                
                if existing.data:
                    # Update existing event
                    self.supabase.table('events').update({
                        'description': event.get('description'),
                        'event_time': event.get('event_time'),
                        'venue': event.get('venue'),
                        'url': event.get('url'),
                        'scraped_at': datetime.now().isoformat()
                    }).eq('id', existing.data[0]['id']).execute()
                else:
                    # Insert new event
                    self.supabase.table('events').insert({
                        'resort_name': resort_name,
                        'event_name': event['event_name'],
                        'event_date': event['event_date'],
                        'event_time': event.get('event_time'),
                        'description': event.get('description'),
                        'event_type': event.get('event_type', 'other'),
                        'venue': event.get('venue'),
                        'url': event.get('url'),
                        'is_major_event': event.get('is_major_event', False),
                        'scraped_at': datetime.now().isoformat()
                    }).execute()
                
                saved_count += 1
                
            except Exception as e:
                print(f"      ⚠️  Error saving event '{event.get('event_name')}': {e}")
                continue
        
        return saved_count
    
    def cleanup_old_events(self):
        """Delete old non-major events (30 days past)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            result = self.supabase.table('events').delete().lt(
                'event_date', cutoff_date
            ).eq('is_major_event', False).execute()
            
            deleted_count = len(result.data) if result.data else 0
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
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY environment variables required")
        sys.exit(1)
    
    orchestrator = ScraperOrchestrator()
    orchestrator.run_all_scrapers()


if __name__ == "__main__":
    main()
