"""
Individual resort scrapers for Colorado mountains
Each scraper extracts events from a specific resort's website
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional

class BaseResortScraper:
    """Base class for all resort scrapers"""
    
    def __init__(self, resort_name: str, events_url: str):
        self.resort_name = resort_name
        self.events_url = events_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.season_end = datetime(2026, 5, 15)  # Scrape through mid-May
        
        # Major event keywords
        self.major_keywords = [
            'winterfest', 'festival', 'fest', 'concert series', 'x games',
            'championship', 'tournament', 'sunsation', 'music festival'
        ]
        
        # Skip keywords
        self.skip_keywords = [
            'kids only', 'children\'s', 'lesson', 'clinic', 'instruction',
            'operating hours', 'hours of operation', 'lift hours'
        ]
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"      Error fetching page: {e}")
            return None
    
    def should_skip_event(self, name: str, description: str = "") -> bool:
        """Check if event should be skipped"""
        text = f"{name} {description}".lower()
        return any(keyword in text for keyword in self.skip_keywords)
    
    def is_major_event(self, name: str, description: str = "") -> bool:
        """Check if event is a major festival/concert"""
        text = f"{name} {description}".lower()
        return any(keyword in text for keyword in self.major_keywords)
    
    def classify_event_type(self, name: str, description: str = "") -> str:
        """Classify event type"""
        text = f"{name} {description}".lower()
        
        if 'festival' in text or 'fest' in text:
            return 'festival'
        elif any(word in text for word in ['concert', 'live music', 'dj', 'band']):
            return 'concert'
        elif any(word in text for word in ['après', 'apres', 'happy hour', 'party']):
            return 'apres'
        elif any(word in text for word in ['competition', 'race', 'championship']):
            return 'competition'
        else:
            return 'other'
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to YYYY-MM-DD format"""
        try:
            for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%b %d, %Y', '%A, %B %d, %Y']:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    if date_obj <= self.season_end:
                        return date_obj.strftime('%Y-%m-%d')
                    return None
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def scrape(self) -> List[Dict]:
        """Override this in each resort scraper"""
        raise NotImplementedError


class CopperScraper(BaseResortScraper):
    """Copper Mountain event scraper"""
    
    def __init__(self):
        super().__init__(
            "Copper Mountain",
            "https://www.coppercolorado.com/events-activities/events-calendar/"
        )
    
    def scrape(self) -> List[Dict]:
        soup = self.fetch_page(self.events_url)
        if not soup:
            return []
        
        events = []
        event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event', re.I))
        
        for container in event_containers[:50]:
            try:
                title = container.find(['h2', 'h3', 'h4'])
                if not title:
                    continue
                
                event_name = title.get_text(strip=True)
                
                # Get date
                date_elem = container.find('time') or container.find(class_=re.compile(r'date', re.I))
                if not date_elem:
                    continue
                date_str = date_elem.get_text(strip=True)
                event_date = self.parse_date(date_str)
                if not event_date:
                    continue
                
                # Get description
                desc_elem = container.find('p')
                description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""
                
                # Skip if needed
                if self.should_skip_event(event_name, description):
                    continue
                
                # Get URL
                link = container.find('a', href=True)
                event_url = f"https://www.coppercolorado.com{link['href']}" if link else self.events_url
                
                events.append({
                    'event_name': event_name,
                    'event_date': event_date,
                    'event_time': None,
                    'description': description,
                    'event_type': self.classify_event_type(event_name, description),
                    'venue': 'Copper Mountain',
                    'url': event_url,
                    'is_major_event': self.is_major_event(event_name, description)
                })
                
            except Exception as e:
                continue
        
        return events


class WinterParkScraper(BaseResortScraper):
    """Winter Park event scraper"""
    
    def __init__(self):
        super().__init__(
            "Winter Park",
            "https://www.winterparkresort.com/things-to-do/events"
        )
    
    def scrape(self) -> List[Dict]:
        soup = self.fetch_page(self.events_url)
        if not soup:
            return []
        
        events = []
        event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event', re.I))
        
        for container in event_containers[:50]:
            try:
                title = container.find(['h2', 'h3', 'h4'])
                if not title:
                    continue
                
                event_name = title.get_text(strip=True)
                date_elem = container.find('time') or container.find(class_=re.compile(r'date', re.I))
                if not date_elem:
                    continue
                
                event_date = self.parse_date(date_elem.get_text(strip=True))
                if not event_date:
                    continue
                
                desc = container.find('p')
                description = desc.get_text(strip=True)[:300] if desc else ""
                
                if self.should_skip_event(event_name, description):
                    continue
                
                link = container.find('a', href=True)
                event_url = f"https://www.winterparkresort.com{link['href']}" if link else self.events_url
                
                events.append({
                    'event_name': event_name,
                    'event_date': event_date,
                    'event_time': None,
                    'description': description,
                    'event_type': self.classify_event_type(event_name, description),
                    'venue': 'Winter Park Resort',
                    'url': event_url,
                    'is_major_event': self.is_major_event(event_name, description)
                })
                
            except Exception as e:
                continue
        
        return events


# Simplified scrapers for other resorts (same pattern)
class EldoraScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Eldora", "https://www.eldora.com/activities-amenities/events/all-events/")
    
    def scrape(self) -> List[Dict]:
        # Similar implementation
        return []


class SteamboatScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Steamboat", "https://www.steamboat.com/events")
    
    def scrape(self) -> List[Dict]:
        return []


class AspenSnowmassScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Aspen Snowmass", "https://www.aspensnowmass.com/visit/events")
    
    def scrape(self) -> List[Dict]:
        return []


class ArapahoeBasinScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Arapahoe Basin", "https://www.arapahoebasin.com/events/")
    
    def scrape(self) -> List[Dict]:
        return []


class KeystoneScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Keystone", "https://www.keystoneresort.com/explore-the-resort/activities-and-events/events-calendar.aspx")
    
    def scrape(self) -> List[Dict]:
        return []


class BreckenridgeScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Breckenridge", "https://www.breckenridge.com/explore-the-resort/activities-and-events/events-activities.aspx")
    
    def scrape(self) -> List[Dict]:
        return []


class VailScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Vail", "https://www.vail.com/explore-the-resort/activities-and-events/vail-events.aspx")
    
    def scrape(self) -> List[Dict]:
        return []


class CrestedButteScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Crested Butte", "https://www.skicb.com/events")
    
    def scrape(self) -> List[Dict]:
        return []


class BeaverCreekScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Beaver Creek", "https://www.beavercreek.com/explore-the-resort/activities/beaver-creek-events.aspx")
    
    def scrape(self) -> List[Dict]:
        return []


class TellurideScraper(BaseResortScraper):
    def __init__(self):
        super().__init__("Telluride", "https://www.tellurideskiresort.com/events")
    
    def scrape(self) -> List[Dict]:
        return []
