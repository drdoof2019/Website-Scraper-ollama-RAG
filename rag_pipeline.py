from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain.schema import Document
from web_scraper import WebScraper
import chromadb
import os

class RAGPipeline:
    def __init__(self, model_name="gemma3:12b"):  # Default model if none specified
        self.scraper = WebScraper()
        try:
            self.llm = OllamaLLM(model=model_name)
        except Exception as e:
            print(f"Error while starting Ollama: {e}")
            print("Make sure the Ollama service is running!")
            raise e
        
        self.embeddings = GPT4AllEmbeddings()
        self.vectorstore = None
        self.qa_chain = None
        
    def process_url(self, url):
        """Process a single URL and add to vectorstore"""
        try:
            print(f"\Processing: {url}")
            content = self.scraper.scrape_single_url(url)
            if content:
                self._process_content(content)
                print("URL processed successfully!")
            else:
                print("Could not retrieve content from URL!")
        except Exception as e:
            print(f"Error while processing URL: {e}")
            
    def process_multiple_urls(self, urls):
        """Process multiple URLs and add to vectorstore"""
        total = len(urls)
        for i, url in enumerate(urls, 1):
            print(f"\Processing: {url} ({i}/{total})")
            self.process_url(url)
            
    def _process_content(self, content):
        """Process content and add to vectorstore"""
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(content['content'])
        
        if not chunks:
            print("Content could not be split!")
            return
            
        # Create Document objects
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": content['url'], "title": content['title']}
            ) for chunk in chunks
        ]
            
        # Initialize vectorstore if not exists
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
        else:
            # Add to existing vectorstore
            self.vectorstore.add_documents(documents)
            
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3})
        )
    
    def chat_loop(self):
        """Interactive chat loop with the model"""
        print("\n=== RAG Chat Started ===")
        print("Type 'quit' or 'exit' to leave")
        print("To add a new document, type 'add url: URL'")
        print("=========================================\n")
        
        while True:
            try:
                question = input("\Q'n: ").strip()
                
                if question.lower() in ['quit', 'exit']:
                    print("\nSee You!")
                    break
                
                if question.lower().startswith('add url:'):
                    # Clean up URL by removing any brackets and extra spaces
                    url = question[8:].strip().strip('[]').strip()
                    if url:
                        print(f"\nProcessing new URL: {url}")
                        self.process_url(url)
                    else:
                        print("You did not enter a valid URL!")
                    continue
                
                if not question:
                    continue
                
                if self.qa_chain is None:
                    print("No content has been loaded yet!")
                    continue
                    
                answer = self.qa_chain.invoke({"query": question})["result"]
                print("\Ans:", answer)
                
            except KeyboardInterrupt:
                print("\n\nSee you soon!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")