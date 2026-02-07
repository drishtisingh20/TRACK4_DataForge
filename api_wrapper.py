"""
API Wrapper for Enterprise Contextual Compression Engine
Provides simplified interface for integration into existing systems
"""

from compression_engine import EnterpriseCompressionEngine
from typing import Dict, Any, Optional, List
import json


class CompressionAPI:
    """
    Simplified API wrapper for the compression engine
    """
    
    def __init__(self, chunk_strategy: str = "paragraph"):
        """
        Initialize the compression API
        
        Args:
            chunk_strategy: Chunking strategy ('paragraph', 'section', 'sentence', 'fixed_size')
        """
        self.engine = EnterpriseCompressionEngine(chunk_strategy=chunk_strategy)
    
    def compress_text(self, text: str) -> Dict[str, Any]:
        """
        Compress a text document
        
        Args:
            text: Document text to compress
            
        Returns:
            Compressed output dictionary
        """
        return self.engine.process(text)
    
    def compress_file(self, filepath: str) -> Dict[str, Any]:
        """
        Compress a document from file
        
        Args:
            filepath: Path to document file
            
        Returns:
            Compressed output dictionary
        """
        document = self.engine.load_document(filepath)
        return self.engine.process(document)
    
    def get_executive_summary(self, text: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Get only the executive summary
        
        Args:
            text: Document text
            max_items: Maximum number of summary items
            
        Returns:
            List of executive summary items
        """
        result = self.engine.process(text)
        return result['executive_compressed_summary'][:max_items]
    
    def get_critical_numbers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract only numbers and limits
        
        Args:
            text: Document text
            
        Returns:
            List of numerical items with traceability
        """
        result = self.engine.process(text)
        return result['numbers_and_limits']
    
    def get_risks_and_compliance(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract only risks and compliance requirements
        
        Args:
            text: Document text
            
        Returns:
            List of risk/compliance items
        """
        result = self.engine.process(text)
        return result['risks_and_constraints']
    
    def get_exceptions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract only exceptions and conditional requirements
        
        Args:
            text: Document text
            
        Returns:
            List of exceptions/conditions
        """
        result = self.engine.process(text)
        return result['exceptions_and_conditions']
    
    def detect_contradictions(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect contradictions in document
        
        Args:
            text: Document text
            
        Returns:
            List of detected contradictions
        """
        result = self.engine.process(text)
        return result['contradictions']
    
    def get_traceability(self, text: str, statement_id: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get traceability mapping
        
        Args:
            text: Document text
            statement_id: Optional specific statement ID to trace
            
        Returns:
            Traceability map or specific trace
        """
        result = self.engine.process(text)
        trace_map = result['traceability_map']
        
        if statement_id:
            return {statement_id: trace_map.get(statement_id, [])}
        return trace_map
    
    def compress_and_save(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Compress document and save to file
        
        Args:
            input_file: Path to input document
            output_file: Path to output JSON file
            
        Returns:
            Compressed output dictionary
        """
        result = self.compress_file(input_file)
        self.engine.save_output(result, output_file)
        return result
    
    def batch_compress(self, documents: List[str]) -> List[Dict[str, Any]]:
        """
        Compress multiple documents
        
        Args:
            documents: List of document texts
            
        Returns:
            List of compressed outputs
        """
        results = []
        for doc in documents:
            results.append(self.engine.process(doc))
        return results
    
    def get_metadata(self, text: str) -> Dict[str, Any]:
        """
        Get compression metadata only
        
        Args:
            text: Document text
            
        Returns:
            Metadata dictionary
        """
        result = self.engine.process(text)
        return result['metadata']
    
    def compare_documents(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Compare two documents by compressing both and highlighting differences
        
        Args:
            doc1: First document text
            doc2: Second document text
            
        Returns:
            Comparison results
        """
        result1 = self.engine.process(doc1)
        result2 = self.engine.process(doc2)
        
        comparison = {
            "document_1": {
                "total_items": result1['metadata']['total_extracted_items'],
                "risks": len(result1['risks_and_constraints']),
                "numbers": len(result1['numbers_and_limits']),
                "contradictions": len(result1['contradictions'])
            },
            "document_2": {
                "total_items": result2['metadata']['total_extracted_items'],
                "risks": len(result2['risks_and_constraints']),
                "numbers": len(result2['numbers_and_limits']),
                "contradictions": len(result2['contradictions'])
            },
            "unique_to_doc1": self._find_unique_items(result1, result2),
            "unique_to_doc2": self._find_unique_items(result2, result1),
            "common_items": self._find_common_items(result1, result2)
        }
        
        return comparison
    
    def _find_unique_items(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> List[str]:
        """Find items unique to result1"""
        items1 = set(item['statement'] for item in result1['executive_compressed_summary'])
        items2 = set(item['statement'] for item in result2['executive_compressed_summary'])
        return list(items1 - items2)
    
    def _find_common_items(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> List[str]:
        """Find items common to both results"""
        items1 = set(item['statement'] for item in result1['executive_compressed_summary'])
        items2 = set(item['statement'] for item in result2['executive_compressed_summary'])
        return list(items1 & items2)


# Example usage patterns
if __name__ == "__main__":
    # Initialize API
    api = CompressionAPI(chunk_strategy="paragraph")
    
    sample_text = """
    The contract specifies a payment of $100,000 due by December 31, 2024.
    However, if payment is delayed, a penalty of 5% per month will apply.
    The maximum penalty shall not exceed $25,000.
    All terms are subject to approval by the board of directors.
    """
    
    # Example 1: Get executive summary only
    print("EXECUTIVE SUMMARY:")
    summary = api.get_executive_summary(sample_text, max_items=5)
    for item in summary:
        print(f"  - {item['statement']}")
    
    # Example 2: Get critical numbers
    print("\nCRITICAL NUMBERS:")
    numbers = api.get_critical_numbers(sample_text)
    for item in numbers:
        print(f"  - {item['statement']} (Value: {item['quote']})")
    
    # Example 3: Get risks
    print("\nRISKS & COMPLIANCE:")
    risks = api.get_risks_and_compliance(sample_text)
    for item in risks:
        print(f"  - {item['statement']}")
    
    # Example 4: Full compression
    print("\nFULL COMPRESSION:")
    result = api.compress_text(sample_text)
    print(f"  Total items extracted: {result['metadata']['total_extracted_items']}")
    print(f"  Compression ratio: {result['metadata']['compression_ratio']}")
