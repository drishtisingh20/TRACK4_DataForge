# Production Integration Guide

## Overview
This guide helps you integrate the Enterprise Contextual Compression Engine into your production systems.

## Architecture Integration Patterns

### 1. REST API Wrapper

```python
from flask import Flask, request, jsonify
from api_wrapper import CompressionAPI

app = Flask(__name__)
api = CompressionAPI()

@app.route('/api/compress', methods=['POST'])
def compress_document():
    """Compress a document via REST API"""
    data = request.get_json()
    document_text = data.get('document')
    chunk_strategy = data.get('chunk_strategy', 'paragraph')
    
    # Reinitialize with strategy
    api = CompressionAPI(chunk_strategy=chunk_strategy)
    
    try:
        result = api.compress_text(document_text)
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/compress/summary', methods=['POST'])
def get_summary():
    """Get executive summary only"""
    data = request.get_json()
    document_text = data.get('document')
    max_items = data.get('max_items', 10)
    
    try:
        summary = api.get_executive_summary(document_text, max_items)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/compress/numbers', methods=['POST'])
def get_numbers():
    """Extract critical numbers only"""
    data = request.get_json()
    document_text = data.get('document')
    
    try:
        numbers = api.get_critical_numbers(document_text)
        return jsonify({
            'status': 'success',
            'numbers': numbers
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. Microservice Architecture

```yaml
# docker-compose.yml
version: '3.8'

services:
  compression-engine:
    build: .
    ports:
      - "5000:5000"
    environment:
      - CHUNK_STRATEGY=paragraph
      - MAX_WORKERS=4
    volumes:
      - ./documents:/app/documents
      - ./outputs:/app/outputs
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY compression_engine.py .
COPY api_wrapper.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "rest_api.py"]
```

### 3. Message Queue Integration

```python
# For AWS SQS, RabbitMQ, or Kafka integration
import json
import boto3
from api_wrapper import CompressionAPI

# Initialize SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.region.amazonaws.com/account/queue-name'

api = CompressionAPI()

def process_message(message):
    """Process a message from queue"""
    body = json.loads(message['Body'])
    
    document_text = body['document']
    output_bucket = body['output_bucket']
    output_key = body['output_key']
    
    # Compress
    result = api.compress_text(document_text)
    
    # Upload to S3
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=json.dumps(result),
        ContentType='application/json'
    )
    
    # Delete message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )

def poll_queue():
    """Poll SQS queue for messages"""
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        
        messages = response.get('Messages', [])
        for message in messages:
            try:
                process_message(message)
            except Exception as e:
                print(f"Error processing message: {e}")

if __name__ == '__main__':
    poll_queue()
```

### 4. Batch Processing

```python
# batch_processor.py
from compression_engine import EnterpriseCompressionEngine
import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

class BatchProcessor:
    """Process multiple documents in parallel"""
    
    def __init__(self, max_workers=4, chunk_strategy='paragraph'):
        self.max_workers = max_workers
        self.chunk_strategy = chunk_strategy
    
    def process_file(self, filepath):
        """Process a single file"""
        engine = EnterpriseCompressionEngine(chunk_strategy=self.chunk_strategy)
        
        # Load document
        with open(filepath, 'r', encoding='utf-8') as f:
            document = f.read()
        
        # Process
        result = engine.process(document)
        
        # Save result
        output_path = filepath.replace('.txt', '_compressed.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        return {
            'input': filepath,
            'output': output_path,
            'items_extracted': result['metadata']['total_extracted_items']
        }
    
    def process_directory(self, directory):
        """Process all files in a directory"""
        files = list(Path(directory).glob('*.txt'))
        
        results = []
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_file, str(f)): f for f in files}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    print(f"Processed: {result['input']} -> {result['items_extracted']} items")
                except Exception as e:
                    print(f"Error processing {futures[future]}: {e}")
        
        return results

# Usage
if __name__ == '__main__':
    processor = BatchProcessor(max_workers=8)
    results = processor.process_directory('/path/to/documents')
    
    # Summary
    print(f"\nProcessed {len(results)} documents")
    print(f"Total items extracted: {sum(r['items_extracted'] for r in results)}")
```

### 5. Database Integration

```python
# database_integration.py
import psycopg2
import json
from api_wrapper import CompressionAPI
from datetime import datetime

class DatabaseIntegration:
    """Store compressed documents in PostgreSQL"""
    
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.api = CompressionAPI()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS compressed_documents (
                    id SERIAL PRIMARY KEY,
                    original_document_id INTEGER,
                    compressed_data JSONB,
                    total_chunks INTEGER,
                    total_items INTEGER,
                    compression_ratio FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    chunk_strategy VARCHAR(50)
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS extracted_items (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES compressed_documents(id),
                    item_type VARCHAR(50),
                    statement TEXT,
                    source_chunks TEXT[],
                    quote TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for fast querying
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_item_type 
                ON extracted_items(item_type)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_id 
                ON extracted_items(document_id)
            """)
            
            self.conn.commit()
    
    def store_compressed_document(self, document_text, original_doc_id=None):
        """Compress and store document"""
        # Compress
        result = self.api.compress_text(document_text)
        
        # Store main document
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO compressed_documents 
                (original_document_id, compressed_data, total_chunks, 
                 total_items, compression_ratio, chunk_strategy)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                original_doc_id,
                json.dumps(result),
                result['metadata']['total_chunks'],
                result['metadata']['total_extracted_items'],
                result['metadata']['compression_ratio'],
                result['metadata']['chunk_strategy']
            ))
            
            doc_id = cur.fetchone()[0]
            
            # Store individual items for querying
            for category in ['numbers_and_limits', 'risks_and_constraints', 
                           'exceptions_and_conditions', 'dates_and_timelines']:
                for item in result.get(category, []):
                    cur.execute("""
                        INSERT INTO extracted_items 
                        (document_id, item_type, statement, source_chunks, quote)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        doc_id,
                        category,
                        item['statement'],
                        item['source_chunks'],
                        item.get('quote', '')
                    ))
            
            self.conn.commit()
        
        return doc_id
    
    def query_by_type(self, item_type, limit=100):
        """Query items by type across all documents"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT statement, source_chunks, quote, created_at
                FROM extracted_items
                WHERE item_type = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (item_type, limit))
            
            return cur.fetchall()
    
    def search_items(self, keyword):
        """Full-text search across all items"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, item_type, statement, source_chunks
                FROM extracted_items
                WHERE statement ILIKE %s
            """, (f'%{keyword}%',))
            
            return cur.fetchall()

# Usage
if __name__ == '__main__':
    db_config = {
        'host': 'localhost',
        'database': 'compression_db',
        'user': 'user',
        'password': 'password'
    }
    
    db = DatabaseIntegration(db_config)
    
    # Store document
    doc_id = db.store_compressed_document("Your document text here...")
    
    # Query by type
    risks = db.query_by_type('risks_and_constraints')
    
    # Search
    results = db.search_items('penalty')
```

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache
import hashlib

class CachedCompressionAPI(CompressionAPI):
    """API with caching for repeated documents"""
    
    @lru_cache(maxsize=1000)
    def compress_text_cached(self, text_hash):
        """Compress with caching by hash"""
        # This would need the actual text stored separately
        pass
    
    def compress_text(self, text):
        """Override to use caching"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # Check cache or process
        return super().compress_text(text)
```

### 2. Async Processing

```python
import asyncio
from compression_engine import EnterpriseCompressionEngine

class AsyncCompressionEngine:
    """Async wrapper for compression engine"""
    
    def __init__(self):
        self.engine = EnterpriseCompressionEngine()
    
    async def process_async(self, document):
        """Process document asynchronously"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.engine.process, 
            document
        )
        return result
    
    async def process_many(self, documents):
        """Process multiple documents concurrently"""
        tasks = [self.process_async(doc) for doc in documents]
        return await asyncio.gather(*tasks)

# Usage
async def main():
    engine = AsyncCompressionEngine()
    documents = ["doc1", "doc2", "doc3"]
    results = await engine.process_many(documents)
    return results

# Run
asyncio.run(main())
```

## Monitoring and Logging

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compression_engine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('compression_engine')

class MonitoredCompressionAPI(CompressionAPI):
    """API with monitoring and metrics"""
    
    def compress_text(self, text):
        """Compress with logging and metrics"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting compression - document length: {len(text)}")
            result = super().compress_text(text)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Compression complete - "
                f"chunks: {result['metadata']['total_chunks']}, "
                f"items: {result['metadata']['total_extracted_items']}, "
                f"duration: {duration}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}", exc_info=True)
            raise
```

## Security Considerations

```python
# Input validation
def validate_input(text, max_length=1000000):
    """Validate input document"""
    if not text or not isinstance(text, str):
        raise ValueError("Document must be a non-empty string")
    
    if len(text) > max_length:
        raise ValueError(f"Document too large (max {max_length} chars)")
    
    # Check for potential injection attacks
    dangerous_patterns = ['<script>', '<?php', 'javascript:']
    if any(pattern in text.lower() for pattern in dangerous_patterns):
        raise ValueError("Document contains potentially dangerous content")
    
    return True

# Rate limiting
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window)
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        """Check if request is allowed"""
        now = datetime.now()
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.time_window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add new request
        self.requests[client_id].append(now)
        return True
```

## Deployment Checklist

- [ ] Set up proper logging and monitoring
- [ ] Configure rate limiting
- [ ] Implement input validation
- [ ] Set up error handling and alerting
- [ ] Configure database backups (if using DB integration)
- [ ] Set up health check endpoints
- [ ] Configure auto-scaling based on load
- [ ] Implement proper authentication/authorization
- [ ] Set up API documentation (Swagger/OpenAPI)
- [ ] Configure CORS policies
- [ ] Set up SSL/TLS certificates
- [ ] Implement request/response caching
- [ ] Configure timeout settings
- [ ] Set up metrics collection (Prometheus, etc.)
- [ ] Implement circuit breakers for external dependencies

## Testing in Production

```python
# Canary deployment test
def canary_test():
    """Test new version with small percentage of traffic"""
    import random
    
    if random.random() < 0.1:  # 10% of traffic
        # Use new version
        api = CompressionAPI(chunk_strategy='section')
    else:
        # Use stable version
        api = CompressionAPI(chunk_strategy='paragraph')
    
    return api
```
