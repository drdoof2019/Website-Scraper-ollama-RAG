# Web Scraper + RAG Tool

A versatile web scraping tool that can extract content from websites, convert it to markdown format, and interact with content using RAG (Retrieval Augmented Generation).

## Features

1. Single URL scraping
2. Bulk URL scraping from a text file
3. Finding and extracting URLs from a webpage
4. Interactive chat with scraped content using RAG

## Installation

1. Make sure you have Python 3.6+ installed
2. Install Ollama from https://ollama.ai/
3. Pull the Gemma model: `ollama pull gemma3:12b`
4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

The tool provides four main functions:

### 1. Scraping a Single URL

To scrape content from a single URL and save it as markdown:

```bash
python main.py single https://example.com -o output_directory
```

### 2. Bulk Scraping from a Text File

To scrape multiple URLs listed in a text file:

```bash
python main.py bulk urls.txt -o output_directory
```

The text file should contain one URL per line.

### 3. Finding URLs in a Webpage

To find all URLs in a webpage and save them to a text file:

```bash
python main.py find https://example.com -o found_urls.txt
```

### 4. Interactive RAG Chat

To start an interactive chat session with scraped content:

```bash
# For single URL (using default model - gemma3:12b):
python interactive_rag.py single https://example.com

# For single URL with specific model:
python interactive_rag.py single https://example.com --model gemma3:12b

# For multiple URLs from a file:
python interactive_rag.py bulk urls.txt

# For multiple URLs with specific model:
python interactive_rag.py bulk urls.txt --model gemma3:12b
```

In the chat session:
- Ask questions about the scraped content
- Add new URLs using: `add url: URL`
- Exit using: `quit` or `exit`

## Available Models

- Any model available in Ollama that supports RAG can be used.
- Make sure to pull the desired model first using: `ollama pull <model_name>`
- Example models: `gemma3:12b`, `llama2`, etc.
- Check the Ollama documentation for a full list of supported models.

## Output

- For single and bulk scraping, the content is saved as markdown files in the specified output directory
- For URL finding, the URLs are saved to a text file
- All markdown files include:
  - Original page title
  - Source URL
  - Main content converted to markdown format

## RAG Pipeline

The tool uses a Retrieval Augmented Generation (RAG) pipeline with:
- Vector store: Chroma
- Embeddings: GPT4All
- LLM: Ollama (Gemma3 12B)

The pipeline:
1. Scrapes web content and converts to markdown
2. Splits content into chunks
3. Creates embeddings and stores in Chroma
4. Uses LLM to generate answers based on retrieved context

## Extending the Tool

The scraper is built with modularity in mind. The `WebScraper` class in `web_scraper.py` can be extended with new methods to add more functionality.
