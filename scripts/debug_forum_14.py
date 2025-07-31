#!/usr/bin/env python3
"""Debug why forum 14 scraping fails"""

import xmlrpc.client
import time
import base64

def decode_base64_field(value):
    """Decode base64 encoded fields from Tapatalk"""
    if isinstance(value, xmlrpc.client.Binary):
        value = value.data
    if isinstance(value, bytes):
        try:
            return base64.b64decode(value).decode('utf-8', errors='ignore')
        except:
            return value.decode('utf-8', errors='ignore')
    return value

def debug_forum_14():
    """Debug forum 14 access"""
    
    proxy = xmlrpc.client.ServerProxy('https://www.net54baseball.com/mobiquo/mobiquo.php')
    
    print("Testing forum 14 access in detail...\n")
    
    try:
        # Get topics from forum 14
        print("1. Attempting to get topics from forum 14...")
        response = proxy.get_topic('14', 0, 4)  # Get 5 topics
        
        if isinstance(response, dict) and response.get('result') == False:
            error = decode_base64_field(response.get('result_text', ''))
            print(f"   ERROR: {error}")
        else:
            print(f"   SUCCESS: Got response")
            
            # Try to parse topics
            if isinstance(response, dict) and 'topics' in response:
                topics = response['topics']
                print(f"   Found {len(topics)} topics")
                
                if topics:
                    # Show first topic
                    topic = topics[0]
                    title = decode_base64_field(topic.get('topic_title', ''))
                    topic_id = topic.get('topic_id', '')
                    print(f"   First topic: ID={topic_id}, Title='{title}'")
            
            elif isinstance(response, list):
                print(f"   Got list response with {len(response)} items")
                if response:
                    topic = response[0]
                    title = decode_base64_field(topic.get('topic_title', ''))
                    print(f"   First topic title: '{title}'")
            
        # Check forum info
        print("\n2. Checking forum info...")
        forum_response = proxy.get_forum('14')
        if isinstance(forum_response, dict):
            forum_name = decode_base64_field(forum_response.get('forum_name', ''))
            print(f"   Forum name: {forum_name}")
            
    except Exception as e:
        print(f"   Exception: {type(e).__name__}: {e}")

if __name__ == '__main__':
    debug_forum_14()