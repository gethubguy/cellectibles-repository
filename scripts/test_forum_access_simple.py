#!/usr/bin/env python3
"""Test which Net54 forums are accessible via Tapatalk API - simplified version"""

import xmlrpc.client
import time

def test_forum_access():
    """Test access to various Net54 forums"""
    
    # Connect to Tapatalk API
    proxy = xmlrpc.client.ServerProxy('https://www.net54baseball.com/mobiquo/mobiquo.php')
    
    # Common forum IDs to test
    forum_ids = [
        4,   # Postwar Baseball Cards (1948-1980ish) B/S/T
        13,  # T3-T207 B/S/T
        14,  # 1920 to 1949 Baseball cards- B/S/T
        39,  # WTB Pre-War Cards
        56,  # Everything Else B/S/T, Non-Sports, etc.
        71,  # Net54 Vintage (PWCC Marquee) Auction
    ]
    
    print("Testing Net54 forum access via Tapatalk API...\n")
    
    for forum_id in forum_ids:
        print(f"Testing forum {forum_id}...", end=" ")
        try:
            time.sleep(1)  # Rate limiting
            
            # Try to get just 1 topic to test access
            response = proxy.get_topic(str(forum_id), 0, 0)
            
            # Check for error response
            if isinstance(response, dict) and response.get('result') == False:
                error_msg = response.get('result_text', b'').decode('utf-8', errors='ignore')
                print(f"✗ RESTRICTED - {error_msg}")
            elif response:
                print(f"✓ ACCESSIBLE")
            else:
                print(f"✗ EMPTY")
                
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
    
    print("\nNote: Forum 14 is likely restricted via Tapatalk API.")
    print("Consider using HTML scraper for restricted forums.")

if __name__ == '__main__':
    test_forum_access()