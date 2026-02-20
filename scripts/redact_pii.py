#!/usr/bin/env python3
"""
PII Redaction Script
Removes personally identifiable information from review CSV files
"""

import re
import csv
import sys
import pandas as pd
from pathlib import Path


class PIIRedactor:
    """Handles PII detection and redaction in text"""
    
    # Regex patterns for PII detection
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone_10digit': r'\b\d{10}\b',
        'phone_formatted': r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'phone_intl': r'\+\d{1,3}[-.\s]?\d{7,14}\b',
        'account_id': r'\b[A-Z0-9]{8,16}\b',  # Potential account/order IDs
        'name_mention': r'\b(my name is|i am|i\'m)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
    }
    
    def __init__(self):
        self.stats = {
            'emails_found': 0,
            'phones_found': 0,
            'names_found': 0,
            'accounts_found': 0
        }
    
    def redact_text(self, text):
        """
        Redact PII from text content
        
        Args:
            text (str): Original text
            
        Returns:
            str: Redacted text
        """
        if not text or pd.isna(text):
            return text
        
        redacted = str(text)
        
        # Redact emails
        if re.search(self.PATTERNS['email'], redacted):
            redacted = re.sub(self.PATTERNS['email'], '[email]', redacted)
            self.stats['emails_found'] += 1
        
        # Redact phone numbers (all formats)
        for phone_pattern in ['phone_10digit', 'phone_formatted', 'phone_intl']:
            if re.search(self.PATTERNS[phone_pattern], redacted):
                redacted = re.sub(self.PATTERNS[phone_pattern], '[phone]', redacted)
                self.stats['phones_found'] += 1
        
        # Redact names mentioned in text (e.g., "My name is John Doe")
        if re.search(self.PATTERNS['name_mention'], redacted, re.IGNORECASE):
            redacted = re.sub(
                self.PATTERNS['name_mention'],
                r'\1 [User]',
                redacted,
                flags=re.IGNORECASE
            )
            self.stats['names_found'] += 1
        
        # Redact potential account IDs (be conservative, only all-caps alphanumeric)
        account_matches = re.findall(r'\b[A-Z0-9]{12,16}\b', redacted)
        if account_matches:
            for match in account_matches:
                # Only redact if it looks like an ID (high entropy)
                if sum(c.isdigit() for c in match) >= 6:  # At least 6 digits
                    redacted = redacted.replace(match, '[ACCOUNT_ID]')
                    self.stats['accounts_found'] += 1
        
        return redacted
    
    def redact_username(self, username):
        """
        Redact or anonymize username
        
        Args:
            username (str): Original username
            
        Returns:
            str: Anonymized username
        """
        if not username or pd.isna(username) or username == 'Anonymous':
            return 'Anonymous'
        
        # Keep first letter, replace rest with asterisks
        if len(username) > 1:
            return username[0] + '*' * min(len(username) - 1, 5)
        return 'User'


def redact_reviews_csv(input_path, output_path):
    """
    Redact PII from reviews CSV file
    
    Args:
        input_path (str): Path to input CSV
        output_path (str): Path to output CSV
    """
    print(f"🔒 Reading reviews from: {input_path}")
    
    # Check if file exists
    if not Path(input_path).exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)
    
    # Read CSV
    try:
        df = pd.read_csv(input_path)
        print(f"✓ Loaded {len(df)} reviews")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_cols = ['rating', 'text', 'date']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Error: Missing required columns: {missing_cols}")
        sys.exit(1)
    
    # Initialize redactor
    redactor = PIIRedactor()
    
    # Redact PII from each column
    print("🔍 Scanning for PII...")
    
    if 'title' in df.columns:
        df['title'] = df['title'].apply(redactor.redact_text)
    
    if 'text' in df.columns:
        df['text'] = df['text'].apply(redactor.redact_text)
    
    if 'username' in df.columns:
        df['username'] = df['username'].apply(redactor.redact_username)
    
    # Save redacted CSV (only keep essential columns)
    output_cols = ['rating', 'title', 'text', 'date']
    output_cols = [col for col in output_cols if col in df.columns]
    
    df_clean = df[output_cols]
    df_clean.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"✓ Saved redacted reviews to: {output_path}")
    
    # Print PII stats
    print("\n📊 PII Redaction Summary:")
    print(f"   - Emails redacted: {redactor.stats['emails_found']}")
    print(f"   - Phone numbers redacted: {redactor.stats['phones_found']}")
    print(f"   - Names redacted: {redactor.stats['names_found']}")
    print(f"   - Account IDs redacted: {redactor.stats['accounts_found']}")
    
    if sum(redactor.stats.values()) == 0:
        print("   ✓ No PII detected (good!)")
    
    # Validation warning
    print("\n⚠️  IMPORTANT: Manually review the output file for any remaining PII!")
    print(f"   Open: {output_path}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Redact PII from review CSV files')
    parser.add_argument(
        '--input',
        type=str,
        default='data/reviews_raw.csv',
        help='Input CSV path (default: data/reviews_raw.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/reviews_clean.csv',
        help='Output CSV path (default: data/reviews_clean.csv)'
    )
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════╗
║   PII Redaction Tool                     ║
║   Anonymize Review Data                  ║
╚══════════════════════════════════════════╝
    """)
    
    # Run redaction
    redact_reviews_csv(args.input, args.output)
    
    print(f"\n✅ Done! Upload this file to n8n:")
    print(f"   → {args.output}")


if __name__ == '__main__':
    main()
