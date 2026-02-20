#!/usr/bin/env python3
"""
Groww App Review Scraper
Fetches reviews from Google Play Store for the Groww investment app
"""

import csv
import sys
from datetime import datetime, timedelta
from google_play_scraper import app, reviews, Sort
import pandas as pd

# Groww app ID on Google Play Store
APP_ID = 'com.nextleap.groww'
APP_NAME = 'Groww'


def scrape_reviews(weeks=12, max_reviews=500):
    """
    Scrape reviews from Google Play Store
    
    Args:
        weeks (int): Number of weeks back to fetch reviews
        max_reviews (int): Maximum number of reviews to fetch
        
    Returns:
        list: List of review dictionaries
    """
    print(f"🔍 Fetching reviews for {APP_NAME} (last {weeks} weeks)...")
    
    try:
        # Fetch reviews (sorted by newest first)
        result, continuation_token = reviews(
            APP_ID,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=max_reviews
        )
        
        print(f"✓ Fetched {len(result)} reviews")
        
        # Calculate date threshold (weeks ago)
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        
        # Filter and format reviews
        filtered_reviews = []
        for review in result:
            review_date = review['at']
            
            # Skip if older than cutoff
            if review_date < cutoff_date:
                continue
            
            # Format review data
            filtered_reviews.append({
                'rating': review['score'],
                'title': (review.get('reviewCreatedVersion') or '')[:100],  # Use version as title placeholder
                'text': (review['content'] or '').strip(),
                'date': review_date.strftime('%Y-%m-%d'),
                'username': review.get('userName', 'Anonymous'),
                'thumbs_up': review.get('thumbsUpCount', 0)
            })
        
        print(f"✓ Filtered to {len(filtered_reviews)} reviews from last {weeks} weeks")
        return filtered_reviews
        
    except Exception as e:
        print(f"❌ Error fetching reviews: {e}")
        sys.exit(1)


def save_to_csv(reviews, output_path='data/reviews_raw.csv'):
    """
    Save reviews to CSV file
    
    Args:
        reviews (list): List of review dictionaries
        output_path (str): Output CSV file path
    """
    if not reviews:
        print("❌ No reviews to save")
        return
    
    # Create DataFrame
    df = pd.DataFrame(reviews)
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"✓ Saved {len(reviews)} reviews to {output_path}")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"   - Total reviews: {len(reviews)}")
    print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   - Average rating: {df['rating'].mean():.1f}/5")
    print(f"   - Rating distribution:")
    for rating in sorted(df['rating'].unique()):
        count = len(df[df['rating'] == rating])
        print(f"     {rating}⭐: {count} reviews")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Groww app reviews from Google Play Store')
    parser.add_argument('--weeks', type=int, default=12, help='Number of weeks back to fetch (default: 12)')
    parser.add_argument('--max', type=int, default=500, help='Maximum reviews to fetch (default: 500)')
    parser.add_argument('--output', type=str, default='data/reviews_raw.csv', help='Output CSV path')
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════╗
║   Groww Review Scraper                   ║
║   Google Play Store → CSV Export         ║
╚══════════════════════════════════════════╝
    """)
    
    # Scrape reviews
    reviews_data = scrape_reviews(weeks=args.weeks, max_reviews=args.max)
    
    # Save to CSV
    if reviews_data:
        save_to_csv(reviews_data, output_path=args.output)
        print(f"\n✅ Done! Next step: Run PII redaction script")
        print(f"   Command: python scripts/redact_pii.py --input {args.output}")
    else:
        print("\n⚠️  No reviews found in the specified time range")


if __name__ == '__main__':
    main()
