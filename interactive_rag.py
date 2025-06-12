from rag_pipeline import RAGPipeline
import argparse

def main():
    parser = argparse.ArgumentParser(description='RAG-enabled Web Scraper')
    parser.add_argument('mode', choices=['single', 'bulk'], help='Scraping mode')
    parser.add_argument('source', help='URL or file containing URLs')
    parser.add_argument('--model', default='gemma3:12b', help='Ollama model to use (default: gemma3:12b)')
    
    args = parser.parse_args()
    
    # Initialize RAG pipeline with specified model
    rag = RAGPipeline(model_name=args.model)
    
    # Process based on mode
    if args.mode == 'single':
        print(f"\nProcessing URL: {args.source}")
        rag.process_url(args.source)
    else:  # bulk mode
        with open(args.source, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"\n{len(urls)} URLs will be processed...")
        rag.process_multiple_urls(urls)
    
    # Start interactive chat
    rag.chat_loop()

if __name__ == '__main__':
    main()
