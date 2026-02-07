"""
Unit tests for Enterprise Contextual Compression Engine
"""

import unittest
import json
from compression_engine import (
    DocumentChunker, 
    CriticalContentExtractor,
    HierarchicalCompressor,
    TraceabilityMapper,
    EnterpriseCompressionEngine,
    ContentType,
    Chunk,
    ExtractedItem
)
from api_wrapper import CompressionAPI


class TestDocumentChunker(unittest.TestCase):
    """Test document chunking functionality"""
    
    def setUp(self):
        self.chunker = DocumentChunker(chunk_strategy="paragraph")
        self.sample_text = """
This is the first paragraph.
It has multiple sentences.

This is the second paragraph.
It also has content.

Third paragraph here.
"""
    
    def test_paragraph_chunking(self):
        """Test paragraph-based chunking"""
        chunks = self.chunker.chunk_document(self.sample_text)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0].chunk_id, "chunk_1")
        
    def test_chunk_ids_sequential(self):
        """Test that chunk IDs are sequential"""
        chunks = self.chunker.chunk_document(self.sample_text)
        for idx, chunk in enumerate(chunks, 1):
            self.assertEqual(chunk.chunk_id, f"chunk_{idx}")
    
    def test_section_chunking(self):
        """Test section-based chunking"""
        chunker = DocumentChunker(chunk_strategy="section")
        text_with_headers = """
# SECTION 1
Content for section 1

# SECTION 2
Content for section 2
"""
        chunks = chunker.chunk_document(text_with_headers)
        self.assertGreater(len(chunks), 0)


class TestCriticalContentExtractor(unittest.TestCase):
    """Test critical content extraction"""
    
    def setUp(self):
        self.extractor = CriticalContentExtractor()
    
    def test_extract_numbers(self):
        """Test number extraction"""
        chunk = Chunk(
            chunk_id="chunk_1",
            content="The price is $150,000 per year with a maximum of 20%.",
            start_pos=0,
            end_pos=100
        )
        items = self.extractor.extract_from_chunk(chunk)
        
        # Should extract both numbers
        number_items = [item for item in items if item.content_type == ContentType.NUMBER_LIMIT]
        self.assertGreater(len(number_items), 0)
    
    def test_extract_dates(self):
        """Test date extraction"""
        chunk = Chunk(
            chunk_id="chunk_1",
            content="The contract starts on January 1, 2024 and ends by 12/31/2025.",
            start_pos=0,
            end_pos=100
        )
        items = self.extractor.extract_from_chunk(chunk)
        
        date_items = [item for item in items if item.content_type == ContentType.DATE_TIMELINE]
        self.assertGreater(len(date_items), 0)
    
    def test_extract_exceptions(self):
        """Test exception extraction"""
        chunk = Chunk(
            chunk_id="chunk_1",
            content="Payment is due within 30 days unless otherwise specified.",
            start_pos=0,
            end_pos=100
        )
        items = self.extractor.extract_from_chunk(chunk)
        
        exception_items = [item for item in items if item.content_type == ContentType.EXCEPTION_CONDITION]
        self.assertGreater(len(exception_items), 0)
    
    def test_extract_risks(self):
        """Test risk extraction"""
        chunk = Chunk(
            chunk_id="chunk_1",
            content="Failure to comply may result in penalties up to $10,000.",
            start_pos=0,
            end_pos=100
        )
        items = self.extractor.extract_from_chunk(chunk)
        
        risk_items = [item for item in items if item.content_type == ContentType.RISK_PENALTY]
        self.assertGreater(len(risk_items), 0)


class TestHierarchicalCompressor(unittest.TestCase):
    """Test hierarchical compression"""
    
    def setUp(self):
        self.compressor = HierarchicalCompressor()
    
    def test_compression_structure(self):
        """Test that compression produces correct structure"""
        items = [
            ExtractedItem(
                statement="Payment of $100,000 is required",
                chunk_id="chunk_1",
                quote="$100,000",
                content_type=ContentType.NUMBER_LIMIT
            ),
            ExtractedItem(
                statement="Deadline is January 1, 2024",
                chunk_id="chunk_2",
                quote="January 1, 2024",
                content_type=ContentType.DATE_TIMELINE
            )
        ]
        
        result = self.compressor.compress(items)
        
        self.assertIn('executive_compressed_summary', result)
        self.assertIn('key_facts', result)
        self.assertIn('numbers_and_limits', result)
        self.assertIn('contradictions', result)
    
    def test_deduplication(self):
        """Test that duplicate items are removed"""
        items = [
            ExtractedItem(
                statement="Payment is $100,000",
                chunk_id="chunk_1",
                quote="$100,000",
                content_type=ContentType.NUMBER_LIMIT
            ),
            ExtractedItem(
                statement="Payment is $100,000",
                chunk_id="chunk_2",
                quote="$100,000",
                content_type=ContentType.NUMBER_LIMIT
            )
        ]
        
        result = self.compressor.compress(items)
        # Should have fewer items due to deduplication
        self.assertLessEqual(len(result['numbers_and_limits']), len(items))


class TestEnterpriseCompressionEngine(unittest.TestCase):
    """Test full compression pipeline"""
    
    def setUp(self):
        self.engine = EnterpriseCompressionEngine()
        self.sample_doc = """
        AGREEMENT
        
        This agreement is effective January 1, 2024.
        The payment amount is $50,000.
        Payment is due within 30 days unless delayed by force majeure.
        Failure to pay may result in penalties.
        """
    
    def test_full_pipeline(self):
        """Test complete processing pipeline"""
        result = self.engine.process(self.sample_doc)
        
        # Check all required sections exist
        self.assertIn('executive_compressed_summary', result)
        self.assertIn('key_facts', result)
        self.assertIn('numbers_and_limits', result)
        self.assertIn('dates_and_timelines', result)
        self.assertIn('exceptions_and_conditions', result)
        self.assertIn('risks_and_constraints', result)
        self.assertIn('contradictions', result)
        self.assertIn('traceability_map', result)
        self.assertIn('explainability', result)
        self.assertIn('metadata', result)
    
    def test_metadata_accuracy(self):
        """Test that metadata is accurate"""
        result = self.engine.process(self.sample_doc)
        metadata = result['metadata']
        
        self.assertGreater(metadata['total_chunks'], 0)
        self.assertGreater(metadata['total_extracted_items'], 0)
        self.assertIsInstance(metadata['compression_ratio'], float)
    
    def test_traceability(self):
        """Test that all items have traceability"""
        result = self.engine.process(self.sample_doc)
        
        # Check that all items in each category have source_chunks
        for category in ['key_facts', 'numbers_and_limits', 'dates_and_timelines']:
            if category in result:
                for item in result[category]:
                    self.assertIn('source_chunks', item)
                    self.assertGreater(len(item['source_chunks']), 0)
    
    def test_no_empty_statements(self):
        """Test that no empty statements are produced"""
        result = self.engine.process(self.sample_doc)
        
        for category in ['executive_compressed_summary', 'key_facts', 'numbers_and_limits']:
            if category in result:
                for item in result[category]:
                    self.assertIsNotNone(item.get('statement'))
                    self.assertGreater(len(item.get('statement', '')), 0)


class TestCompressionAPI(unittest.TestCase):
    """Test API wrapper functionality"""
    
    def setUp(self):
        self.api = CompressionAPI()
        self.sample_text = """
        Payment of $100,000 is due by December 31, 2024.
        Late payments will incur a 5% penalty.
        This applies unless payment is delayed by circumstances beyond control.
        """
    
    def test_compress_text(self):
        """Test text compression"""
        result = self.api.compress_text(self.sample_text)
        self.assertIsInstance(result, dict)
        self.assertIn('metadata', result)
    
    def test_get_executive_summary(self):
        """Test executive summary extraction"""
        summary = self.api.get_executive_summary(self.sample_text, max_items=5)
        self.assertIsInstance(summary, list)
        self.assertLessEqual(len(summary), 5)
    
    def test_get_critical_numbers(self):
        """Test number extraction via API"""
        numbers = self.api.get_critical_numbers(self.sample_text)
        self.assertIsInstance(numbers, list)
        
        # Should find at least the $100,000 and 5%
        self.assertGreater(len(numbers), 0)
    
    def test_get_exceptions(self):
        """Test exception extraction via API"""
        exceptions = self.api.get_exceptions(self.sample_text)
        self.assertIsInstance(exceptions, list)
        
        # Should find the "unless" clause
        self.assertGreater(len(exceptions), 0)
    
    def test_detect_contradictions(self):
        """Test contradiction detection via API"""
        contradictions = self.api.detect_contradictions(self.sample_text)
        self.assertIsInstance(contradictions, list)
    
    def test_get_metadata(self):
        """Test metadata retrieval"""
        metadata = self.api.get_metadata(self.sample_text)
        self.assertIn('total_chunks', metadata)
        self.assertIn('total_extracted_items', metadata)
        self.assertIn('compression_ratio', metadata)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.engine = EnterpriseCompressionEngine()
    
    def test_empty_document(self):
        """Test handling of empty document"""
        result = self.engine.process("")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['metadata']['total_chunks'], 0)
    
    def test_very_short_document(self):
        """Test handling of very short document"""
        result = self.engine.process("Hello.")
        self.assertIsInstance(result, dict)
    
    def test_document_with_special_characters(self):
        """Test handling of special characters"""
        doc = "Payment: $1,000.00 (USD) — due by 12/31/2024!"
        result = self.engine.process(doc)
        self.assertGreater(result['metadata']['total_extracted_items'], 0)
    
    def test_document_with_unicode(self):
        """Test handling of unicode characters"""
        doc = "Payment is €50,000 by décembre 31, 2024"
        result = self.engine.process(doc)
        self.assertIsInstance(result, dict)
    
    def test_very_long_document(self):
        """Test handling of very long document"""
        # Create a long document
        long_doc = " ".join(["This is sentence number {}.".format(i) for i in range(1000)])
        result = self.engine.process(long_doc)
        self.assertGreater(result['metadata']['total_chunks'], 10)


class TestChunkingStrategies(unittest.TestCase):
    """Test different chunking strategies"""
    
    def setUp(self):
        self.sample_doc = """
# SECTION 1
Content for section one.

# SECTION 2
Content for section two.

Some additional content.
"""
    
    def test_paragraph_strategy(self):
        """Test paragraph chunking strategy"""
        engine = EnterpriseCompressionEngine(chunk_strategy="paragraph")
        result = engine.process(self.sample_doc)
        self.assertGreater(result['metadata']['total_chunks'], 0)
    
    def test_section_strategy(self):
        """Test section chunking strategy"""
        engine = EnterpriseCompressionEngine(chunk_strategy="section")
        result = engine.process(self.sample_doc)
        self.assertGreater(result['metadata']['total_chunks'], 0)
    
    def test_sentence_strategy(self):
        """Test sentence chunking strategy"""
        engine = EnterpriseCompressionEngine(chunk_strategy="sentence")
        result = engine.process(self.sample_doc)
        self.assertGreater(result['metadata']['total_chunks'], 0)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
