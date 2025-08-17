#!/usr/bin/env python3
"""
Test script for the Link Ingestor system.
This script demonstrates how to use the system to ingest a web page.
"""

import asyncio
import json
from app.domain.services.ingest_service import IngestService


async def test_ingestion():
    """Test the link ingestion system with a sample URL."""
    
    # Test URL - you can change this to any website
    test_url = "https://httpbin.org/html"
    
    print(f"🚀 Testing Link Ingestor with URL: {test_url}")
    print("=" * 60)
    
    try:
        # Create ingestion service
        ingest_service = IngestService()
        
        # Get summary first
        print("📊 Getting ingestion summary...")
        summary = await ingest_service.get_ingestion_summary(test_url)
        
        if "error" in summary:
            print(f"❌ Error getting summary: {summary['error']}")
            return
        
        print(f"✅ Summary retrieved successfully!")
        print(f"   Title: {summary.get('title', 'N/A')}")
        print(f"   Description: {summary.get('description', 'N/A')[:100]}...")
        print(f"   Total links found: {summary.get('total_links_found', 0)}")
        print(f"   External links: {summary.get('external_links', 0)}")
        print(f"   Internal links: {summary.get('internal_links', 0)}")
        print()
        
        # Perform full ingestion
        print("🔍 Starting full page ingestion...")
        result = await ingest_service.ingest_page(test_url)
        
        if result.job.status == "completed":
            print(f"✅ Ingestion completed successfully!")
            print(f"   Total links extracted: {result.total_links}")
            print(f"   Total backlinks found: {result.total_backlinks}")
            print()
            
            # Display some sample links
            if result.links:
                print("🔗 Sample extracted links:")
                for i, link in enumerate(result.links[:5]):  # Show first 5
                    print(f"   {i+1}. {link.url}")
                    print(f"      Domain: {link.domain}")
                    print(f"      Type: {'External' if link.link_type == 'external' else 'Internal'}")
                    if link.link_text:
                        print(f"      Text: {link.link_text[:50]}...")
                    print()
            
            # Display some sample backlinks
            if result.backlinks:
                print("🔗 Sample backlinks:")
                for i, backlink in enumerate(result.backlinks[:3]):  # Show first 3
                    print(f"   {i+1}. {backlink.backlink_url}")
                    print(f"      Domain: {backlink.backlink_domain}")
                    if backlink.backlink_title:
                        print(f"      Title: {backlink.backlink_title[:50]}...")
                    print()
        else:
            print(f"❌ Ingestion failed: {result.job.error_message}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_multiple_urls():
    """Test the system with multiple URLs."""
    
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    print("🧪 Testing multiple URLs...")
    print("=" * 60)
    
    ingest_service = IngestService()
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        try:
            summary = await ingest_service.get_ingestion_summary(url)
            if "error" not in summary:
                print(f"   ✅ Links found: {summary.get('total_links_found', 0)}")
            else:
                print(f"   ❌ Error: {summary['error']}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")


def main():
    """Main function to run the tests."""
    print("🔗 Link Ingestor System Test")
    print("=" * 60)
    
    # Run the main test
    asyncio.run(test_ingestion())
    
    print("\n" + "=" * 60)
    
    # Run multiple URL test
    asyncio.run(test_multiple_urls())
    
    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    main()


