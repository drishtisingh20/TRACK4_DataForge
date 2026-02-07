# 🚀 Quick Start Guide

## Enterprise Contextual Compression Engine

A production-ready preprocessing pipeline that extracts decision-critical information from documents while maintaining full traceability.

---

## 📥 Installation

```bash
# No dependencies required - uses Python standard library
# Python 3.7+ required

# Verify installation
python compression_engine.py --help
```

---

## ⚡ 30-Second Start

```python
from compression_engine import EnterpriseCompressionEngine

# 1. Create engine
engine = EnterpriseCompressionEngine()

# 2. Process document
document = open("my_document.txt").read()
result = engine.process(document)

# 3. Access results
print(f"Found {result['metadata']['total_extracted_items']} critical items")
print(result['executive_compressed_summary'])
```

---

## 🎯 Common Use Cases

### 1. Contract Analysis - Extract Key Terms

```python
from api_wrapper import CompressionAPI

api = CompressionAPI()
contract = open("contract.txt").read()

# Get all monetary values
numbers = api.get_critical_numbers(contract)
for item in numbers:
    print(f"💰 {item['quote']}: {item['statement']}")

# Get all deadlines
dates = api.compress_text(contract)['dates_and_timelines']
for item in dates:
    print(f"📅 {item['quote']}: {item['statement']}")

# Find exceptions and conditions
exceptions = api.get_exceptions(contract)
for item in exceptions:
    print(f"⚠️  {item['statement']}")
```

### 2. Compliance Check - Find Risks

```python
policy = open("policy_document.txt").read()

# Extract compliance requirements and risks
risks = api.get_risks_and_compliance(policy)
for item in risks:
    print(f"🚨 {item['statement']}")
    print(f"   Source: {item['source_chunks']}")
```

### 3. Document Comparison

```python
old_doc = open("version_1.txt").read()
new_doc = open("version_2.txt").read()

comparison = api.compare_documents(old_doc, new_doc)

print("Added in new version:")
for item in comparison['unique_to_doc2']:
    print(f"  + {item}")

print("\nRemoved from old version:")
for item in comparison['unique_to_doc1']:
    print(f"  - {item}")
```

### 4. Generate Visual Dashboard

```python
from dashboard_generator import DashboardGenerator

generator = DashboardGenerator()
generator.generate_dashboard(document, "output.html")

# Open output.html in browser for interactive visualization
```

---

## 📊 Output Structure

Every processed document returns a structured JSON with:

```json
{
  "executive_compressed_summary": [...],  // Top 10 most critical items
  "numbers_and_limits": [...],            // $$$, %, thresholds
  "dates_and_timelines": [...],           // Deadlines, dates
  "exceptions_and_conditions": [...],     // "unless", "only if"
  "risks_and_constraints": [...],         // Penalties, requirements
  "contradictions": [...],                // Conflicting statements
  "traceability_map": {...},              // Statement -> source mapping
  "metadata": {
    "total_chunks": 27,
    "total_extracted_items": 45,
    "compression_ratio": 0.15
  }
}
```

---

## 🔧 Configuration Options

### Chunking Strategies

```python
# Default: paragraph-based
engine = EnterpriseCompressionEngine(chunk_strategy="paragraph")

# For structured docs with headers
engine = EnterpriseCompressionEngine(chunk_strategy="section")

# For fine-grained analysis
engine = EnterpriseCompressionEngine(chunk_strategy="sentence")
```

### Custom Processing

```python
# Process with custom settings
result = engine.process(document)

# Filter results by type
high_priority = [
    item for item in result['executive_compressed_summary']
    if item['priority'] in ['risk_penalty', 'compliance_requirement']
]

# Filter by confidence (for facts)
high_confidence_facts = [
    item for item in result['key_facts']
    if item.get('confidence', 1.0) > 0.8
]
```

---

## 📁 File Operations

### Process File

```python
# Command line
python compression_engine.py input.txt output.json

# Python API
engine = EnterpriseCompressionEngine()
document = engine.load_document("input.txt")
result = engine.process(document)
engine.save_output(result, "output.json")
```

### Batch Processing

```python
from pathlib import Path

documents = list(Path("./documents").glob("*.txt"))
for doc_path in documents:
    document = open(doc_path).read()
    result = engine.process(document)
    
    output_path = str(doc_path).replace(".txt", "_compressed.json")
    engine.save_output(result, output_path)
    
    print(f"✅ {doc_path.name}: {result['metadata']['total_extracted_items']} items")
```

---

## 🧪 Testing

```bash
# Run example
python example_usage.py

# Run tests
python test_compression_engine.py

# Generate dashboard
python dashboard_generator.py
```

---

## 🎨 What Gets Extracted?

### ✅ EXTRACTED (Decision-Critical)
- Numbers, amounts, percentages
- Dates, deadlines, timelines
- Exceptions ("unless", "except", "only if")
- Mandatory requirements ("must", "shall", "required")
- Penalties, fines, violations
- Compliance requirements
- Objective facts with specific details

### ❌ IGNORED (Non-Critical)
- Background explanations
- Narrative descriptions
- Generic statements
- Filler text
- Examples and illustrations
- Historical context (unless containing dates)

---

## 🔍 Traceability

Every extracted item links back to source:

```python
result = engine.process(document)

# Get statement ID from traceability map
stmt_id = "stmt_5"
source_chunks = result['traceability_map'][stmt_id]

# Find what was extracted and why
for explain in result['explainability']:
    if explain['source_chunk'] in source_chunks:
        print(f"Statement: {explain['statement']}")
        print(f"Reason: {explain['included_because']}")
        print(f"Type: {explain['content_type']}")
```

---

## 🚨 Important Rules

1. **Zero Hallucination**: Only extracts what's explicitly present
2. **Exact Preservation**: Numbers and dates never modified
3. **Full Traceability**: Every statement links to source
4. **Contradiction Surfacing**: Conflicts shown, not hidden
5. **No Narrative**: Background text excluded

---

## 💡 Pro Tips

1. **Choose the right chunking strategy**
   - `paragraph` for general documents
   - `section` for structured docs with headers
   - `sentence` for maximum granularity

2. **Check contradictions first**
   - Often reveal important nuances
   - May indicate errors in source document

3. **Use traceability for verification**
   - Don't trust blindly - verify critical items
   - Link back to source for context

4. **Combine multiple categories**
   - Numbers + Dates = Financial timeline
   - Risks + Exceptions = Complete compliance picture

5. **Review explainability**
   - Understand what was excluded and why
   - Adjust extraction if needed

---

## 📞 Next Steps

- **Read full docs**: `README.md`
- **Production deployment**: `INTEGRATION_GUIDE.md`
- **View examples**: `example_usage.py`
- **See visualization**: `dashboard_generator.py`
- **Run tests**: `test_compression_engine.py`

---

## 🎓 Example Workflow

```python
# Complete workflow example
from api_wrapper import CompressionAPI
from dashboard_generator import DashboardGenerator

# 1. Initialize
api = CompressionAPI(chunk_strategy="paragraph")

# 2. Load document
contract = open("employment_contract.txt").read()

# 3. Quick analysis
print("EXECUTIVE SUMMARY:")
summary = api.get_executive_summary(contract, max_items=5)
for item in summary:
    print(f"  • {item['statement'][:100]}...")

print("\nCRITICAL NUMBERS:")
numbers = api.get_critical_numbers(contract)
for item in numbers:
    print(f"  💰 {item['quote']}: {item['statement'][:80]}...")

print("\nRISKS IDENTIFIED:")
risks = api.get_risks_and_compliance(contract)
for item in risks[:5]:
    print(f"  🚨 {item['statement'][:80]}...")

# 4. Check for conflicts
contradictions = api.detect_contradictions(contract)
if contradictions:
    print(f"\n⚠️  {len(contradictions)} contradictions detected!")

# 5. Generate visual report
generator = DashboardGenerator()
generator.generate_dashboard(contract, "contract_analysis.html")
print("\n✅ Dashboard saved to contract_analysis.html")

# 6. Save full results
result = api.compress_text(contract)
api.engine.save_output(result, "contract_compressed.json")
print("✅ Full results saved to contract_compressed.json")
```

---

**You're ready to go! 🎉**

For questions or issues, check the documentation or example files.
