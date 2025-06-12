from web_scraper import WebScraper
import argparse
import os

def format_markdown_output(result):
    """Format scraped content as markdown"""
    return f"# {result['title']}\n\nSource: {result['url']}\n\n---\n\n{result['content']}"

def main():
    parser = argparse.ArgumentParser(description='Web Scraper Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Single URL scrape
    single_parser = subparsers.add_parser('single', help='Scrape a single URL')
    single_parser.add_argument('url', help='URL to scrape')
    single_parser.add_argument('-o', '--output', help='Output directory for markdown files or "llm" for direct output', default='output')
    single_parser.add_argument('--raw', action='store_true', help='Return raw markdown output without saving to file')

    # Bulk URL scrape
    bulk_parser = subparsers.add_parser('bulk', help='Scrape URLs from a text file')
    bulk_parser.add_argument('file', help='Text file containing URLs (one per line)')
    bulk_parser.add_argument('-o', '--output', help='Output directory for markdown files or "llm" for direct output', default='output')
    bulk_parser.add_argument('--raw', action='store_true', help='Return raw markdown output without saving to file')

    # Find URLs
    find_parser = subparsers.add_parser('find', help='Find URLs in a webpage')
    find_parser.add_argument('url', help='URL to search for links')
    find_parser.add_argument('-o', '--output', help='Output file for found URLs', default='found_urls.txt')

    args = parser.parse_args()
    scraper = WebScraper()

    if args.command == 'single':
        result = scraper.scrape_single_url(args.url)
        if result:
            if args.output == "llm" or args.raw:
                # Format content for direct LLM consumption or raw output
                print(format_markdown_output(result))
            else:
                saved_file = scraper.save_markdown(result, args.output)
                if saved_file:
                    print(f"Content saved to: {saved_file}")
                else:
                    print("Failed to save content")
        else:
            print("Failed to scrape URL")

    elif args.command == 'bulk':
        results = scraper.scrape_urls_from_file(args.file)
        if results:
            if args.output == "llm" or args.raw:
                # Print all results as markdown with separators
                for i, result in enumerate(results):
                    if i > 0:
                        print("\n\n" + "="*80 + "\n\n")  # Separator between documents
                    print(format_markdown_output(result))
                    content_lengths = [len(r['content']) for r in results if 'content' in r]
                    print("Total content length: {} characters".format(sum(content_lengths)))
            else:
                for result in results:
                    saved_file = scraper.save_markdown(result, args.output)
                    if saved_file:
                        print(f"Content saved to: {saved_file}")
                    else:
                        print(f"Failed to save content for {result['url']}")
        
            print("Scraping completed. Found {} URLs.".format(len(results)))
            
            #print("Scraped content lengths: {}".format(content_lengths))
            
        else:
            print("No URLs were successfully scraped")

    elif args.command == 'find':
        urls = scraper.find_urls_in_page(args.url)
        if urls:
            if scraper.save_urls_to_file(urls, args.output):
                print(f"Found {len(urls)} URLs, saved to: {args.output}")
            else:
                print("Failed to save URLs to file")
        else:
            print("No URLs found")

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
