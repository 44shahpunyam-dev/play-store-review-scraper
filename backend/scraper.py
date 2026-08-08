from google_play_scraper import reviews, Sort
from datetime import datetime, date
import time


class ReviewScraper:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
    
    def scrape(self, package_id: str, from_date: date, to_date: date, rating: int = 0, hint: str = ""):
        """
        Scrape reviews from Google Play Store with pagination.
        
        Args:
            package_id: Package ID (e.g., com.example.app)
            from_date: Start date (datetime.date object)
            to_date: End date (datetime.date object)
            rating: 0 for all, 1-5 for specific rating
            hint: Optional text that must appear at end of review
        
        Returns:
            List of filtered review dictionaries
        """
        all_reviews = []
        continuation_token = None
        
        try:
            # Fetch all reviews with pagination
            while True:
                try:
                    # Scrape a batch of reviews
                    batch, continuation_token = reviews(
                        package_id,
                        lang='en',
                        country='in',
                        sort=Sort.NEWEST,
                        count=100,
                        continuation_token=continuation_token
                    )
                    
                    if not batch:
                        break
                    
                    last_review_date_obj = None

                    # Process each review in batch
                    for review in batch:
                        # Parse review timestamp to date
                        try:
                            review_timestamp = review.get('at')
                            if isinstance(review_timestamp, datetime):
                                review_datetime = review_timestamp
                                review_date_obj = review_datetime.date()
                            elif isinstance(review_timestamp, (int, float)):
                                review_datetime = datetime.fromtimestamp(review_timestamp / 1000.0)
                                review_date_obj = review_datetime.date()
                            else:
                                continue
                        except Exception:
                            continue
                        
                        last_review_date_obj = review_date_obj

                        # Check if review is within date range
                        if review_date_obj < from_date or review_date_obj > to_date:
                            continue
                        
                        # Check rating filter
                        review_rating = review.get('score', 0)
                        if rating != 0 and review_rating != rating:
                            continue
                        
                        # Check hint filter (must be at end of review)
                        review_text = review.get('content', '')
                        if hint:
                            if not self._matches_hint(review_text, hint):
                                continue
                        
                        # Format review data
                        formatted_review = {
                            'User': review.get('userName', 'Unknown'),
                            'Review': review.get('content', ''),
                            'Package ID': package_id,
                            'Rating': f"{review_rating}/5",
                            'Date': review_date_obj.strftime('%Y-%m-%d'),
                            'Time': review_datetime.strftime('%H:%M:%S')
                        }
                        
                        all_reviews.append(formatted_review)
                    
                    # If we've gone past our date range, we can stop
                    if last_review_date_obj and last_review_date_obj < from_date:
                        break
                    
                    # Stop if no continuation token (no more pages)
                    if not continuation_token:
                        break
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                
                except Exception as e:
                    print(f"Error fetching batch: {str(e)}")
                    break
            
            return all_reviews
        
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            raise Exception(f"Failed to scrape reviews: {str(e)}")
    
    def _matches_hint(self, review_text: str, hint: str) -> bool:
        """
        Check if hint appears at the END of review text.
        Matching is case-insensitive for text, exact for emojis/symbols.
        Also ensures exact count (e.g. '...' will not match '....').
        
        Args:
            review_text: The review content
            hint: The hint to search for at the end
        
        Returns:
            True if hint is found at the end of review
        """
        if not hint:
            return True
        
        # Strip trailing whitespace from review
        cleaned_review = review_text.rstrip()
        cleaned_hint = hint.rstrip()
        
        if not cleaned_hint or not cleaned_review:
            return False
            
        review_len = len(cleaned_review)
        hint_len = len(cleaned_hint)
        
        if review_len < hint_len:
            return False
            
        # Check end match
        is_unicode = any(ord(char) > 127 for char in cleaned_hint)
        if is_unicode:
            ends = cleaned_review.endswith(cleaned_hint)
        else:
            ends = cleaned_review.lower().endswith(cleaned_hint.lower())
            
        if not ends:
            return False
            
        # Check preceding character to prevent extra repeated characters (e.g. '...' matching '....')
        start_idx = review_len - hint_len
        if start_idx > 0:
            preceding_char = cleaned_review[start_idx - 1]
            first_hint_char = cleaned_hint[0]
            if is_unicode:
                if preceding_char == first_hint_char:
                    return False
            else:
                if preceding_char.lower() == first_hint_char.lower():
                    return False
                    
        return True
