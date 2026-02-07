"""
Enterprise Contextual Compression Engine
A preprocessing pipeline for extracting decision-critical information with full traceability
"""

import re
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ContentType(Enum):
    """Types of decision-critical content"""
    OBJECTIVE_FACT = "objective_fact"
    NUMBER_LIMIT = "number_limit"
    DATE_TIMELINE = "date_timeline"
    EXCEPTION_CONDITION = "exception_condition"
    RISK_PENALTY = "risk_penalty"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    CONTRADICTION = "contradiction"


@dataclass
class Chunk:
    """Represents a logical chunk of the document"""
    chunk_id: str
    content: str
    start_pos: int
    end_pos: int


@dataclass
class ExtractedItem:
    """Represents a single extracted decision-critical item"""
    statement: str
    chunk_id: str
    quote: str
    content_type: ContentType
    confidence: float = 1.0


@dataclass
class CompressedStatement:
    """Final compressed statement with traceability"""
    statement: str
    source_chunks: List[str]
    quote: str = ""
    content_type: str = ""


class DocumentChunker:
    """Splits document into logical chunks"""
    
    def __init__(self, chunk_strategy: str = "paragraph"):
        """
        Args:
            chunk_strategy: 'paragraph', 'section', 'sentence', or 'fixed_size'
        """
        self.chunk_strategy = chunk_strategy
    
    def chunk_document(self, text: str, max_chunk_size: int = 1000) -> List[Chunk]:
        """Split document into logical chunks"""
        
        if self.chunk_strategy == "paragraph":
            return self._chunk_by_paragraph(text)
        elif self.chunk_strategy == "section":
            return self._chunk_by_section(text)
        elif self.chunk_strategy == "sentence":
            return self._chunk_by_sentence(text)
        elif self.chunk_strategy == "fixed_size":
            return self._chunk_by_fixed_size(text, max_chunk_size)
        else:
            return self._chunk_by_paragraph(text)
    
    def _chunk_by_paragraph(self, text: str) -> List[Chunk]:
        """Split by paragraphs (double newline or clear breaks)"""
        # Split on double newlines or multiple spaces/newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_pos = 0
        
        for idx, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            chunk = Chunk(
                chunk_id=f"chunk_{idx + 1}",
                content=para,
                start_pos=current_pos,
                end_pos=current_pos + len(para)
            )
            chunks.append(chunk)
            current_pos += len(para)
        
        return chunks
    
    def _chunk_by_section(self, text: str) -> List[Chunk]:
        """Split by headers or section markers"""
        # Look for headers (lines with #, all caps, numbered sections, etc.)
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_pos = 0
        chunk_idx = 1
        
        header_pattern = r'^(#{1,6}\s|[A-Z\s]{10,}$|\d+\.\s+[A-Z]|SECTION|ARTICLE)'
        
        for line in lines:
            if re.match(header_pattern, line.strip()) and current_chunk:
                # Start new chunk
                content = '\n'.join(current_chunk).strip()
                if content:
                    chunk = Chunk(
                        chunk_id=f"chunk_{chunk_idx}",
                        content=content,
                        start_pos=current_pos,
                        end_pos=current_pos + len(content)
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                    current_pos += len(content)
                
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            content = '\n'.join(current_chunk).strip()
            if content:
                chunk = Chunk(
                    chunk_id=f"chunk_{chunk_idx}",
                    content=content,
                    start_pos=current_pos,
                    end_pos=current_pos + len(content)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_sentence(self, text: str) -> List[Chunk]:
        """Split by sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_pos = 0
        
        for idx, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            chunk = Chunk(
                chunk_id=f"chunk_{idx + 1}",
                content=sentence,
                start_pos=current_pos,
                end_pos=current_pos + len(sentence)
            )
            chunks.append(chunk)
            current_pos += len(sentence)
        
        return chunks
    
    def _chunk_by_fixed_size(self, text: str, max_size: int) -> List[Chunk]:
        """Split by fixed character size with sentence boundary awareness"""
        chunks = []
        current_pos = 0
        chunk_idx = 1
        
        while current_pos < len(text):
            end_pos = min(current_pos + max_size, len(text))
            
            # Try to break at sentence boundary
            chunk_text = text[current_pos:end_pos]
            last_period = chunk_text.rfind('.')
            
            if last_period > max_size * 0.5:  # At least 50% of chunk size
                end_pos = current_pos + last_period + 1
                chunk_text = text[current_pos:end_pos]
            
            chunk = Chunk(
                chunk_id=f"chunk_{chunk_idx}",
                content=chunk_text.strip(),
                start_pos=current_pos,
                end_pos=end_pos
            )
            chunks.append(chunk)
            
            current_pos = end_pos
            chunk_idx += 1
        
        return chunks


class CriticalContentExtractor:
    """Extracts decision-critical information from chunks"""
    
    def __init__(self):
        # Patterns for different types of critical content
        self.number_patterns = [
            r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:%|percent|dollars?|\$|€|£|USD|EUR|GBP)\b',
            r'\b(?:maximum|minimum|max|min|up to|at least|no more than|threshold|limit)\s+\d+',
            r'\b\d+\s*(?:days|hours|minutes|months|years|weeks)\b',
        ]
        
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:by|before|after|until|from|effective)\s+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}\b',
        ]
        
        self.exception_patterns = [
            r'\b(?:unless|except|excluding|with the exception of|only if|provided that|subject to)\b',
            r'\b(?:however|but|although|whereas|notwithstanding)\b',
            r'\b(?:if and only if|conditional upon|contingent on)\b',
        ]
        
        self.risk_patterns = [
            r'\b(?:penalty|fine|violation|breach|non-compliance|failure to|risk|liability|damages)\b',
            r'\b(?:must|shall|required|mandatory|obligated|prohibited|forbidden)\b',
            r'\b(?:may result in|subject to|punishable by)\b',
        ]
        
        self.compliance_patterns = [
            r'\b(?:comply|compliance|regulation|regulatory|standard|requirement|pursuant to)\b',
            r'\b(?:certif[iy]|audit|inspection|verification|validation)\b',
        ]
    
    def extract_from_chunk(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract all decision-critical items from a single chunk"""
        items = []
        
        # Extract numbers and limits
        items.extend(self._extract_numbers(chunk))
        
        # Extract dates and timelines
        items.extend(self._extract_dates(chunk))
        
        # Extract exceptions and conditions
        items.extend(self._extract_exceptions(chunk))
        
        # Extract risks and penalties
        items.extend(self._extract_risks(chunk))
        
        # Extract compliance requirements
        items.extend(self._extract_compliance(chunk))
        
        # Extract objective facts (sentences with factual assertions)
        items.extend(self._extract_facts(chunk))
        
        return items
    
    def _extract_numbers(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract numerical limits, thresholds, and values"""
        items = []
        
        for pattern in self.number_patterns:
            matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
            for match in matches:
                # Get surrounding context (sentence)
                context = self._get_sentence_context(chunk.content, match.start())
                
                item = ExtractedItem(
                    statement=context.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=match.group(0),
                    content_type=ContentType.NUMBER_LIMIT
                )
                items.append(item)
        
        return items
    
    def _extract_dates(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract dates and timeline information"""
        items = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
            for match in matches:
                context = self._get_sentence_context(chunk.content, match.start())
                
                item = ExtractedItem(
                    statement=context.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=match.group(0),
                    content_type=ContentType.DATE_TIMELINE
                )
                items.append(item)
        
        return items
    
    def _extract_exceptions(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract exceptions and conditional statements"""
        items = []
        
        for pattern in self.exception_patterns:
            matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
            for match in matches:
                context = self._get_sentence_context(chunk.content, match.start())
                
                item = ExtractedItem(
                    statement=context.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=match.group(0),
                    content_type=ContentType.EXCEPTION_CONDITION
                )
                items.append(item)
        
        return items
    
    def _extract_risks(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract risks, penalties, and mandatory requirements"""
        items = []
        
        for pattern in self.risk_patterns:
            matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
            for match in matches:
                context = self._get_sentence_context(chunk.content, match.start())
                
                item = ExtractedItem(
                    statement=context.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=match.group(0),
                    content_type=ContentType.RISK_PENALTY
                )
                items.append(item)
        
        return items
    
    def _extract_compliance(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract compliance and regulatory requirements"""
        items = []
        
        for pattern in self.compliance_patterns:
            matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
            for match in matches:
                context = self._get_sentence_context(chunk.content, match.start())
                
                item = ExtractedItem(
                    statement=context.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=match.group(0),
                    content_type=ContentType.COMPLIANCE_REQUIREMENT
                )
                items.append(item)
        
        return items
    
    def _extract_facts(self, chunk: Chunk) -> List[ExtractedItem]:
        """Extract objective factual statements"""
        items = []
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', chunk.content)
        
        # Indicators of objective facts
        fact_indicators = [
            r'\b(?:is|are|was|were|will be|has been|have been)\b',
            r'\b(?:defines|means|refers to|indicates|specifies)\b',
            r'\b(?:includes|consists of|comprises)\b',
        ]
        
        for sentence in sentences:
            # Check if sentence contains fact indicators
            is_fact = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in fact_indicators)
            
            # Also check if it's not too vague
            is_specific = any(re.search(pattern, sentence) for pattern in self.number_patterns + self.date_patterns)
            
            if is_fact and len(sentence.split()) > 5:  # Minimum length
                item = ExtractedItem(
                    statement=sentence.strip(),
                    chunk_id=chunk.chunk_id,
                    quote=sentence[:50] + "..." if len(sentence) > 50 else sentence,
                    content_type=ContentType.OBJECTIVE_FACT,
                    confidence=0.8 if is_specific else 0.6
                )
                items.append(item)
        
        return items
    
    def _get_sentence_context(self, text: str, position: int) -> str:
        """Get the full sentence containing the position"""
        # Find sentence boundaries
        start = text.rfind('.', 0, position)
        if start == -1:
            start = 0
        else:
            start += 1
        
        end = text.find('.', position)
        if end == -1:
            end = len(text)
        else:
            end += 1
        
        return text[start:end].strip()


class HierarchicalCompressor:
    """Compresses extracted items into hierarchical representation"""
    
    def compress(self, items: List[ExtractedItem]) -> Dict[str, Any]:
        """Compress extracted items with deduplication and hierarchy"""
        
        # Group by content type
        grouped = self._group_by_type(items)
        
        # Deduplicate within groups
        deduplicated = self._deduplicate_items(grouped)
        
        # Build hierarchical structure
        compressed = {
            "executive_compressed_summary": self._build_executive_summary(deduplicated),
            "key_facts": self._format_items(deduplicated.get(ContentType.OBJECTIVE_FACT, [])),
            "numbers_and_limits": self._format_items(deduplicated.get(ContentType.NUMBER_LIMIT, [])),
            "dates_and_timelines": self._format_items(deduplicated.get(ContentType.DATE_TIMELINE, [])),
            "exceptions_and_conditions": self._format_items(deduplicated.get(ContentType.EXCEPTION_CONDITION, [])),
            "risks_and_constraints": self._format_items(
                deduplicated.get(ContentType.RISK_PENALTY, []) + 
                deduplicated.get(ContentType.COMPLIANCE_REQUIREMENT, [])
            ),
            "contradictions": self._detect_contradictions(items)
        }
        
        return compressed
    
    def _group_by_type(self, items: List[ExtractedItem]) -> Dict[ContentType, List[ExtractedItem]]:
        """Group items by content type"""
        grouped = {}
        for item in items:
            if item.content_type not in grouped:
                grouped[item.content_type] = []
            grouped[item.content_type].append(item)
        return grouped
    
    def _deduplicate_items(self, grouped: Dict[ContentType, List[ExtractedItem]]) -> Dict[ContentType, List[ExtractedItem]]:
        """Remove duplicate or highly similar items"""
        deduplicated = {}
        
        for content_type, items in grouped.items():
            unique_items = []
            seen_statements = set()
            
            for item in items:
                # Normalize statement for comparison
                normalized = self._normalize_statement(item.statement)
                
                if normalized not in seen_statements:
                    seen_statements.add(normalized)
                    unique_items.append(item)
                else:
                    # Merge chunk references if duplicate
                    for existing in unique_items:
                        if self._normalize_statement(existing.statement) == normalized:
                            # This is handled in formatting stage
                            break
            
            deduplicated[content_type] = unique_items
        
        return deduplicated
    
    def _normalize_statement(self, statement: str) -> str:
        """Normalize statement for comparison"""
        # Remove extra whitespace, lowercase, remove punctuation at end
        normalized = re.sub(r'\s+', ' ', statement.lower().strip())
        normalized = re.sub(r'[.!?]+$', '', normalized)
        return normalized
    
    def _format_items(self, items: List[ExtractedItem]) -> List[Dict[str, Any]]:
        """Format items into output structure"""
        formatted = []
        
        for item in items:
            formatted.append({
                "statement": item.statement,
                "source_chunks": [item.chunk_id],
                "quote": item.quote,
                "content_type": item.content_type.value
            })
        
        return formatted
    
    def _build_executive_summary(self, deduplicated: Dict[ContentType, List[ExtractedItem]]) -> List[Dict[str, Any]]:
        """Build high-level executive summary"""
        summary = []
        
        # Prioritize: risks > numbers > dates > exceptions > facts
        priority_order = [
            ContentType.RISK_PENALTY,
            ContentType.COMPLIANCE_REQUIREMENT,
            ContentType.NUMBER_LIMIT,
            ContentType.DATE_TIMELINE,
            ContentType.EXCEPTION_CONDITION,
            ContentType.OBJECTIVE_FACT
        ]
        
        for content_type in priority_order:
            items = deduplicated.get(content_type, [])
            # Take top items by confidence
            top_items = sorted(items, key=lambda x: x.confidence, reverse=True)[:3]
            
            for item in top_items:
                summary.append({
                    "statement": item.statement,
                    "source_chunks": [item.chunk_id],
                    "priority": content_type.value
                })
        
        return summary[:10]  # Top 10 most critical items
    
    def _detect_contradictions(self, items: List[ExtractedItem]) -> List[Dict[str, Any]]:
        """Detect contradictory statements"""
        contradictions = []
        
        # Group by similar topics (simple keyword matching)
        # This is a basic implementation - could be enhanced with NLP
        
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                if self._might_contradict(item1, item2):
                    contradictions.append({
                        "statement_1": item1.statement,
                        "source_chunk_1": item1.chunk_id,
                        "statement_2": item2.statement,
                        "source_chunk_2": item2.chunk_id,
                        "contradiction_type": "potential_conflict"
                    })
        
        return contradictions
    
    def _might_contradict(self, item1: ExtractedItem, item2: ExtractedItem) -> bool:
        """Simple contradiction detection"""
        # Look for same keywords but different numbers/values
        words1 = set(re.findall(r'\b\w+\b', item1.statement.lower()))
        words2 = set(re.findall(r'\b\w+\b', item2.statement.lower()))
        
        overlap = words1 & words2
        
        # If significant word overlap but different chunks and different numbers
        if len(overlap) > 3:
            nums1 = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', item1.statement)
            nums2 = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', item2.statement)
            
            if nums1 and nums2 and nums1 != nums2:
                return True
        
        return False


class TraceabilityMapper:
    """Builds traceability and explainability structures"""
    
    def build_traceability_map(self, compressed: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build statement-to-chunk mapping"""
        traceability = {}
        
        statement_id = 1
        
        # Map all compressed items
        for category in ["executive_compressed_summary", "key_facts", "numbers_and_limits", 
                        "dates_and_timelines", "exceptions_and_conditions", "risks_and_constraints"]:
            if category in compressed:
                for item in compressed[category]:
                    key = f"stmt_{statement_id}"
                    traceability[key] = item.get("source_chunks", [])
                    statement_id += 1
        
        return traceability
    
    def build_explainability(self, items: List[ExtractedItem], chunks: List[Chunk]) -> List[Dict[str, Any]]:
        """Build explainability for inclusion/exclusion decisions"""
        explainability = []
        
        # Document what was included
        for item in items:
            explainability.append({
                "statement": item.statement[:100] + "..." if len(item.statement) > 100 else item.statement,
                "included_because": self._get_inclusion_reason(item),
                "source_chunk": item.chunk_id,
                "content_type": item.content_type.value,
                "removed_content_reason": None
            })
        
        # Document what was excluded (sample of generic content)
        for chunk in chunks[:5]:  # Sample first 5 chunks
            generic_content = self._identify_generic_content(chunk)
            if generic_content:
                explainability.append({
                    "statement": generic_content[:100] + "...",
                    "included_because": None,
                    "source_chunk": chunk.chunk_id,
                    "content_type": "excluded",
                    "removed_content_reason": "Generic narrative or background content without decision-critical information"
                })
        
        return explainability
    
    def _get_inclusion_reason(self, item: ExtractedItem) -> str:
        """Get reason for including this item"""
        reasons = {
            ContentType.OBJECTIVE_FACT: "Contains objective factual assertion",
            ContentType.NUMBER_LIMIT: "Contains specific numerical threshold or limit",
            ContentType.DATE_TIMELINE: "Contains date or timeline information",
            ContentType.EXCEPTION_CONDITION: "Contains exception or conditional requirement",
            ContentType.RISK_PENALTY: "Contains risk, penalty, or mandatory requirement",
            ContentType.COMPLIANCE_REQUIREMENT: "Contains compliance or regulatory requirement"
        }
        return reasons.get(item.content_type, "Decision-critical information")
    
    def _identify_generic_content(self, chunk: Chunk) -> str:
        """Identify generic/narrative content that was excluded"""
        # Look for introductory phrases, background info
        generic_patterns = [
            r'^(?:This document|This section|The purpose|Background|Introduction|Overview)',
            r'(?:for example|such as|including but not limited to)',
            r'(?:In general|Generally speaking|Typically)'
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, chunk.content, re.IGNORECASE)
            if match:
                # Return the sentence containing this pattern
                sentences = re.split(r'(?<=[.!?])\s+', chunk.content)
                for sentence in sentences:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        return sentence
        
        return ""


class EnterpriseCompressionEngine:
    """Main orchestrator for the compression pipeline"""
    
    def __init__(self, chunk_strategy: str = "paragraph"):
        self.chunker = DocumentChunker(chunk_strategy)
        self.extractor = CriticalContentExtractor()
        self.compressor = HierarchicalCompressor()
        self.tracer = TraceabilityMapper()
    
    def process(self, document: str) -> Dict[str, Any]:
        """
        Main processing pipeline
        
        Args:
            document: Input document text
            
        Returns:
            Complete compressed output with traceability
        """
        # Step 1: Chunk the document
        chunks = self.chunker.chunk_document(document)
        
        # Step 2: Extract decision-critical content from each chunk
        all_items = []
        for chunk in chunks:
            items = self.extractor.extract_from_chunk(chunk)
            all_items.extend(items)
        
        # Step 3: Hierarchical compression
        compressed = self.compressor.compress(all_items)
        
        # Step 4: Build traceability and explainability
        compressed["traceability_map"] = self.tracer.build_traceability_map(compressed)
        compressed["explainability"] = self.tracer.build_explainability(all_items, chunks)
        
        # Add metadata
        compressed["metadata"] = {
            "total_chunks": len(chunks),
            "total_extracted_items": len(all_items),
            "compression_ratio": self._calculate_compression_ratio(document, compressed),
            "chunk_strategy": self.chunker.chunk_strategy
        }
        
        return compressed
    
    def _calculate_compression_ratio(self, original: str, compressed: Dict[str, Any]) -> float:
        """Calculate compression ratio"""
        original_size = len(original)
        compressed_size = len(json.dumps(compressed))
        return round(compressed_size / original_size, 3) if original_size > 0 else 0.0
    
    def save_output(self, output: Dict[str, Any], filepath: str):
        """Save compressed output to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def load_document(self, input_file):
        with open(input_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read()



# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compression_engine.py <input_file> [output_file] [chunk_strategy]")
        print("Chunk strategies: paragraph (default), section, sentence, fixed_size")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "compressed_output.json"
    chunk_strategy = sys.argv[3] if len(sys.argv) > 3 else "paragraph"
    
    # Initialize engine
    engine = EnterpriseCompressionEngine(chunk_strategy=chunk_strategy)
    
    # Load document
    print(f"Loading document from {input_file}...")
    document = engine.load_document(input_file)
    
    # Process
    print("Processing document...")
    result = engine.process(document)
    
    # Save
    print(f"Saving compressed output to {output_file}...")
    engine.save_output(result, output_file)
    
    # Print summary
    print("\n=== Compression Summary ===")
    print(f"Total chunks: {result['metadata']['total_chunks']}")
    print(f"Total extracted items: {result['metadata']['total_extracted_items']}")
    print(f"Compression ratio: {result['metadata']['compression_ratio']}")
    print(f"Executive summary items: {len(result['executive_compressed_summary'])}")
    print(f"Key facts: {len(result['key_facts'])}")
    print(f"Numbers/limits: {len(result['numbers_and_limits'])}")
    print(f"Dates/timelines: {len(result['dates_and_timelines'])}")
    print(f"Exceptions/conditions: {len(result['exceptions_and_conditions'])}")
    print(f"Risks/constraints: {len(result['risks_and_constraints'])}")
    print(f"Contradictions detected: {len(result['contradictions'])}")
    print(f"\nOutput saved to: {output_file}")
