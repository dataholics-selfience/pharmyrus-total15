#!/usr/bin/env python3
"""
Standalone test script to inspect Google Patents HTML structure
Run this locally to see actual selectors and save full HTML for analysis
"""
import asyncio
from playwright.async_api import async_playwright

async def inspect_patent_page(patent_id: str):
    """Inspect and save HTML of a patent page for analysis"""
    
    print(f"🔍 Inspecting Google Patents page for: {patent_id}")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Run in visible mode
            slow_mo=1000     # Slow down for observation
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        url = f"https://patents.google.com/patent/{patent_id}/en"
        
        print(f"📍 Navigating to: {url}")
        await page.goto(url, timeout=60000, wait_until='networkidle')
        
        print("⏳ Waiting 5 seconds for page to load...")
        await page.wait_for_timeout(5000)
        
        # Save full HTML
        html = await page.content()
        html_file = f"patent_{patent_id}_full.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Saved full HTML to: {html_file}")
        
        # Take screenshot
        screenshot_file = f"patent_{patent_id}_screenshot.png"
        await page.screenshot(path=screenshot_file, full_page=True)
        print(f"📸 Saved screenshot to: {screenshot_file}")
        
        # Try to find Patent Family tab
        print("\n" + "=" * 70)
        print("🔍 SEARCHING FOR PATENT FAMILY TAB")
        print("=" * 70)
        
        tab_selectors = [
            'a:has-text("Patent family")',
            'a:has-text("Family")',
            'button:has-text("Patent family")',
            'button:has-text("Family")',
            '[data-tab="family"]',
            '#family-tab',
            'a[href*="family"]',
            '.tab-family'
        ]
        
        for selector in tab_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    html_snippet = await elem.evaluate('el => el.outerHTML')
                    print(f"\n✅ FOUND: {selector}")
                    print(f"   Text: {text}")
                    print(f"   HTML: {html_snippet[:200]}...")
                    
                    # Click it
                    print(f"   🖱️  Clicking tab...")
                    await elem.click()
                    
                    # Wait for content
                    print(f"   ⏳ Waiting 30 seconds for family content...")
                    await page.wait_for_timeout(30000)
                    
                    # Save HTML after click
                    html_after = await page.content()
                    html_after_file = f"patent_{patent_id}_after_family_click.html"
                    with open(html_after_file, 'w', encoding='utf-8') as f:
                        f.write(html_after)
                    print(f"   💾 Saved HTML after click to: {html_after_file}")
                    
                    # Screenshot after click
                    screenshot_after = f"patent_{patent_id}_family_tab.png"
                    await page.screenshot(path=screenshot_after, full_page=True)
                    print(f"   📸 Screenshot after click: {screenshot_after}")
                    
                    break
            except Exception as e:
                print(f"❌ {selector}: {e}")
        
        # Search for tables
        print("\n" + "=" * 70)
        print("🔍 SEARCHING FOR TABLES")
        print("=" * 70)
        
        tables = await page.query_selector_all('table')
        print(f"Found {len(tables)} tables on page")
        
        for i, table in enumerate(tables):
            try:
                # Get table classes and id
                table_class = await table.get_attribute('class') or 'no-class'
                table_id = await table.get_attribute('id') or 'no-id'
                
                # Get first row to see headers
                rows = await table.query_selector_all('tr')
                first_row = await rows[0].inner_text() if rows else 'empty'
                
                print(f"\n📊 Table {i+1}:")
                print(f"   Class: {table_class}")
                print(f"   ID: {table_id}")
                print(f"   Rows: {len(rows)}")
                print(f"   First row: {first_row[:100]}...")
                
                # If looks like patent family table
                if any(keyword in first_row.lower() for keyword in ['publication', 'filing', 'country', 'number']):
                    print(f"   ⭐ THIS LOOKS LIKE PATENT FAMILY TABLE!")
                    
                    # Extract first 3 data rows
                    print(f"   📋 Sample data:")
                    for j in range(min(3, len(rows)-1)):
                        try:
                            row_data = await rows[j+1].inner_text()
                            print(f"      Row {j+1}: {row_data[:150]}")
                        except:
                            pass
            except Exception as e:
                print(f"   ❌ Error inspecting table {i+1}: {e}")
        
        # Search for all links with /patent/
        print("\n" + "=" * 70)
        print("🔍 SEARCHING FOR PATENT LINKS")
        print("=" * 70)
        
        patent_links = await page.query_selector_all('a[href*="/patent/"]')
        print(f"Found {len(patent_links)} patent links")
        
        # Show first 10
        for i, link in enumerate(patent_links[:10]):
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                print(f"   {i+1}. {text[:50]} -> {href[:80]}")
            except:
                pass
        
        print("\n" + "=" * 70)
        print("✅ INSPECTION COMPLETE")
        print("=" * 70)
        print(f"\nFiles saved:")
        print(f"  - {html_file}")
        print(f"  - {screenshot_file}")
        print(f"  - {html_after_file} (if tab was found)")
        print(f"  - {screenshot_after} (if tab was found)")
        print(f"\n📧 Send these files for analysis if needed!")
        
        # Keep browser open for manual inspection
        print("\n⏸️  Browser will stay open for 60 seconds for manual inspection...")
        await page.wait_for_timeout(60000)
        
        await browser.close()

if __name__ == "__main__":
    # Test with the problematic patent
    patent_id = "BR112012008823B8"
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     GOOGLE PATENTS HTML INSPECTOR                            ║
║     For debugging patent family extraction                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(inspect_patent_page(patent_id))
