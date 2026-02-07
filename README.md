# Enterprise Contextual Compression Engine

A production-grade preprocessing pipeline for compressing large documents while preserving all decision-critical information and maintaining full traceability to source content.

## 🎯 What This Is NOT

This is **NOT** traditional summarization. This system:
- **Extracts** decision-critical facts, not summaries
- **Preserves** exact numbers, dates, conditions, and exceptions
- **Maintains** full traceability to source chunks
- **Surfaces** contradictions explicitly
- **Zero hallucination** - only extracts what's present

## 🏗️ Architecture

```
Document Input
    ↓
[Document Chunker] → Logical chunks with IDs
    ↓
[Critical Content Extractor] → Extract facts, numbers, dates, exceptions, risks
    ↓
[Hierarchical Compressor] → Deduplicate & organize
    ↓
[Traceability Mapper] → Build source mappings
    ↓
Structured JSON Output
```

## 📦 Components

### 1. DocumentChunker
Splits documents into logical chunks with unique IDs.

**Strategies:**
- `paragraph`: Split on double newlines (default)
- `section`: Split on headers/section markers
- `sentence`: Split on sentence boundaries
- `fixed_size`: Fixed character size with sentence awareness

### 2. CriticalContentExtractor
Extracts decision-critical information using pattern matching and NLP heuristics.

**Extracts:**
- ✅ Numbers, limits, thresholds
- ✅ Dates and timelines
- ✅ Exceptions and conditions ("unless", "except", "only if")
- ✅ Risks, penalties, mandatory requirements
- ✅ Compliance requirements
- ✅ Objective facts

**Ignores:**
- ❌ Background explanations
- ❌ Narrative descriptions
- ❌ Generic text
- ❌ Filler content

### 3. HierarchicalCompressor
Deduplicates and organizes extracted items into hierarchical structure.

### 4. TraceabilityMapper
Builds bidirectional mappings between statements and source chunks.

## 🚀 Quick Start

### Basic Usage

```python
from compression_engine import EnterpriseCompressionEngine

# Initialize engine
engine = EnterpriseCompressionEngine(chunk_strategy="paragraph")

# Process document
document = "Your long document text here..."
result = engine.process(document)

# Access compressed data
print(result['executive_compressed_summary'])
print(result['numbers_and_limits'])
print(result['risks_and_constraints'])
```

### Using the API Wrapper

```python
from api_wrapper import CompressionAPI

api = CompressionAPI()

# Get executive summary only
summary = api.get_executive_summary(document_text, max_items=10)

# Get critical numbers
numbers = api.get_critical_numbers(document_text)

# Detect contradictions
contradictions = api.detect_contradictions(document_text)

# Full compression with save
result = api.compress_and_save("input.txt", "output.json")
```

### Command Line

```bash
# Basic usage
python compression_engine.py input.txt output.json

# With specific chunking strategy
python compression_engine.py input.txt output.json section

# Run example
python example_usage.py
```

### Web Dashboard with LLM Summarization & Chat

Upload documents to get an **LLM-generated summary** and **chat with the LLM** about the document (e.g. books, PDFs). Uses **Google AI Studio (Gemini)**.

1. **Get a Google AI Studio API key** (free) at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).  
   - Enter it in the "Google AI Studio API Key" field on the dashboard, or  
   - Set the environment variable: `GEMINI_API_KEY=your-key` (or `GOOGLE_API_KEY`)

2. **Install and run:**
   ```bash
   py -m pip install flask google-genai PyPDF2 python-docx
   py app.py
   ```
   Open http://127.0.0.1:5000

3. **Flow:** Enter API key → Upload file (.txt, .pdf, .docx) → Click "Summarize with LLM" → View **LLM Summary** tab and extracted tabs → Use **Chat** to ask the LLM questions about the document.

## 📋 Output Structure

```json
{
  "executive_compressed_summary": [
    {
      "statement": "The Company shall pay Employee a base salary of $150,000 per year",
      "source_chunks": ["chunk_2"],
      "priority": "number_limit"
    }
  ],
  "key_facts": [
    {
      "statement": "Employee shall serve as Senior Software Engineer",
      "source_chunks": ["chunk_1"],
      "quote": "Senior Software Engineer",
      "content_type": "objective_fact"
    }
  ],
  "numbers_and_limits": [
    {
      "statement": "The Company shall pay Employee a base salary of $150,000 per year",
      "source_chunks": ["chunk_2"],
      "quote": "$150,000",
      "content_type": "number_limit"
    }
  ],
  "dates_and_timelines": [
    {
      "statement": "This Agreement shall commence on January 1, 2024",
      "source_chunks": ["chunk_4"],
      "quote": "January 1, 2024",
      "content_type": "date_timeline"
    }
  ],
  "exceptions_and_conditions": [
    {
      "statement": "Benefits are only available to employees who maintain active employment status",
      "source_chunks": ["chunk_3"],
      "quote": "only",
      "content_type": "exception_condition"
    }
  ],
  "risks_and_constraints": [
    {
      "statement": "Violation of confidentiality provisions may result in damages up to $500,000",
      "source_chunks": ["chunk_5"],
      "quote": "may result in",
      "content_type": "risk_penalty"
    }
  ],
  "contradictions": [
    {
      "statement_1": "Options vest over 4 years",
      "source_chunk_1": "chunk_9",
      "statement_2": "25% after first year",
      "source_chunk_2": "chunk_9",
      "contradiction_type": "potential_conflict"
    }
  ],
  "traceability_map": {
    "stmt_1": ["chunk_2"],
    "stmt_2": ["chunk_1"],
    "stmt_3": ["chunk_4"]
  },
  "explainability": [
    {
      "statement": "The Company shall pay Employee a base salary of $150,000 per year",
      "included_because": "Contains specific numerical threshold or limit",
      "source_chunk": "chunk_2",
      "content_type": "number_limit",
      "removed_content_reason": null
    }
  ],
  "metadata": {
    "total_chunks": 10,
    "total_extracted_items": 45,
    "compression_ratio": 0.234,
    "chunk_strategy": "paragraph"
  }
}
```

## 🔧 Configuration

### Chunking Strategies

**Paragraph (Default)**
- Best for: General documents, contracts, reports
- Splits on: Double newlines or paragraph breaks
```python
engine = EnterpriseCompressionEngine(chunk_strategy="paragraph")
```

**Section**
- Best for: Structured documents with headers
- Splits on: Headers, numbered sections, all-caps titles
```python
engine = EnterpriseCompressionEngine(chunk_strategy="section")
```

**Sentence**
- Best for: Fine-grained analysis
- Splits on: Sentence boundaries
```python
engine = EnterpriseCompressionEngine(chunk_strategy="sentence")
```

**Fixed Size**
- Best for: Very long documents, processing limits
- Splits on: Fixed character count with sentence awareness
```python
engine = EnterpriseCompressionEngine(chunk_strategy="fixed_size")
```

## 📊 Use Cases

### 1. Contract Analysis
```python
api = CompressionAPI()
contract = open("employment_contract.txt").read()

# Get all financial terms
numbers = api.get_critical_numbers(contract)

# Get all exceptions and conditions
exceptions = api.get_exceptions(contract)

# Detect conflicting terms
contradictions = api.detect_contradictions(contract)
```

### 2. Regulatory Compliance
```python
regulation_doc = open("regulation.txt").read()

# Extract compliance requirements
compliance = api.get_risks_and_compliance(regulation_doc)

# Get all dates and deadlines
deadlines = api.get_critical_numbers(regulation_doc)
```

### 3. Document Comparison
```python
old_policy = open("policy_v1.txt").read()
new_policy = open("policy_v2.txt").read()

comparison = api.compare_documents(old_policy, new_policy)
print(comparison['unique_to_doc2'])  # What changed?
```

### 4. Batch Processing
```python
documents = [doc1, doc2, doc3, doc4, doc5]
results = api.batch_compress(documents)

for idx, result in enumerate(results):
    print(f"Document {idx}: {result['metadata']['total_extracted_items']} items")
```

## 🎛️ Advanced Features

### Custom Extraction Patterns

You can extend the `CriticalContentExtractor` with custom patterns:

```python
from compression_engine import CriticalContentExtractor

class CustomExtractor(CriticalContentExtractor):
    def __init__(self):
        super().__init__()
        # Add custom patterns
        self.custom_patterns = [
            r'\b(?:critical|urgent|important)\b',
            r'\bSLA\s+\d+%',
        ]
```

### Custom Content Types

```python
from compression_engine import ContentType, ExtractedItem

# Define custom content type
class CustomContentType(ContentType):
    SLA_REQUIREMENT = "sla_requirement"
    SECURITY_CONTROL = "security_control"
```

### Filtering Results

```python
result = engine.process(document)

# Filter by confidence
high_confidence = [
    item for item in result['key_facts'] 
    if item.get('confidence', 1.0) > 0.8
]

# Filter by content type
only_risks = [
    item for item in result['risks_and_constraints']
    if 'penalty' in item['statement'].lower()
]
```

## 🔍 Traceability Example

Every statement can be traced back to source:

```python
result = engine.process(document)

# Get traceability for specific statement
stmt_id = "stmt_5"
source_chunks = result['traceability_map'][stmt_id]

# Find original content
for chunk in chunks:
    if chunk.chunk_id in source_chunks:
        print(f"Original: {chunk.content}")
```

## ⚠️ Important Rules

1. **No Hallucination**: System only extracts what's explicitly present
2. **Preserve Exactness**: Numbers, dates, and terms are never modified
3. **Maintain Traceability**: Every statement links to source chunks
4. **Surface Contradictions**: Conflicts are shown, not resolved
5. **Exclude Narrative**: Background and explanations are removed

## 🧪 Testing

```bash
# Run example with sample document
python example_usage.py

# Test with your own document
python compression_engine.py my_document.txt output.json

# Test different strategies
python compression_engine.py my_document.txt output_para.json paragraph
python compression_engine.py my_document.txt output_sect.json section
```

## 📈 Performance Metrics

The system provides compression metrics:

- **Compression Ratio**: Output size / Input size
- **Extraction Rate**: Items extracted / Total chunks
- **Coverage**: Percentage of chunks with extracted items

## 🛠️ Requirements

```
Python 3.7+
No external dependencies required (uses standard library only)
```

## 📝 License

MIT License - Free for commercial and personal use

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional extraction patterns
- ML-based extraction models
- Multi-language support
- PDF/DOCX parsing integration
- Visualization dashboard

## 📞 Support

For issues or questions:
1. Check the example scripts
2. Review the output JSON structure
3. Examine the explainability section for inclusion/exclusion reasons

## 🎓 Best Practices

1. **Choose the right chunking strategy** for your document type
2. **Review contradictions** - they often reveal important nuances
3. **Use traceability** to verify extracted content
4. **Combine multiple categories** for comprehensive analysis
5. **Test with sample documents** before production use

## 🔮 Roadmap

- [ ] ML-based extraction models
- [ ] Multi-language support
- [ ] PDF/DOCX direct parsing
- [ ] Web UI dashboard
- [ ] Real-time streaming processing
- [ ] Integration with document management systems
- [ ] Enhanced contradiction detection with NLP
- [ ] Confidence scoring improvements
