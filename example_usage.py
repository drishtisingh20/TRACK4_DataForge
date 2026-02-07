"""
Example usage of the Enterprise Contextual Compression Engine
"""

from compression_engine import EnterpriseCompressionEngine
import json

# Sample complex document for testing
SAMPLE_DOCUMENT = """
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into effective January 1, 2024, between TechCorp Inc. ("Company") and John Smith ("Employee").

1. POSITION AND DUTIES

Employee shall serve as Senior Software Engineer. The Employee will report directly to the Chief Technology Officer. Employee agrees to devote their full professional time and attention to the performance of their duties.

2. COMPENSATION

The Company shall pay Employee a base salary of $150,000 per year, payable in accordance with the Company's standard payroll schedule. Employee shall be eligible for an annual performance bonus of up to 20% of base salary, subject to achievement of performance objectives.

3. BENEFITS

Employee shall be entitled to participate in all employee benefit plans maintained by the Company, including health insurance, 401(k) retirement plan with 4% company match, and 15 days paid time off per year.

However, benefits are only available to employees who maintain active employment status. If employment is terminated for cause, benefits cease immediately.

4. TERM AND TERMINATION

This Agreement shall commence on January 1, 2024 and continue until terminated by either party. Either party may terminate this Agreement with 30 days written notice.

The Company may terminate employment immediately for cause, including but not limited to: misconduct, breach of confidentiality, or violation of company policies. Unless terminated for cause, Employee shall receive severance pay equal to 2 months base salary.

5. CONFIDENTIALITY

Employee agrees to maintain confidentiality of all proprietary information. This obligation shall survive termination and continue for a period of 5 years after termination date.

Violation of confidentiality provisions may result in legal action and damages up to $500,000.

6. NON-COMPETE

Employee agrees not to work for direct competitors within a 50-mile radius of Company headquarters for a period of 12 months following termination.

This restriction applies only if Employee is terminated without cause or resigns voluntarily. It does not apply if Employee is terminated for reasons beyond their control, such as company restructuring or layoffs.

7. INTELLECTUAL PROPERTY

All inventions, discoveries, and creative works developed during employment shall be the exclusive property of the Company. Employee must disclose all such works within 30 days of creation.

8. PERFORMANCE REVIEWS

Employee will receive performance reviews quarterly. Minimum performance threshold is 3.0 out of 5.0. Failure to maintain minimum threshold for two consecutive quarters may result in termination.

However, the Annual Review in December carries triple weight and can override quarterly scores.

9. STOCK OPTIONS

Employee shall be granted 10,000 stock options at a strike price of $10.00 per share. Options vest over 4 years: 25% after first year, then monthly thereafter. All unvested options are forfeited upon termination unless terminated without cause.

10. AMENDMENT

This Agreement may only be amended by written consent of both parties. No verbal agreements or modifications shall be valid.
"""

def main():
    # Initialize the compression engine
    print("=" * 60)
    print("ENTERPRISE CONTEXTUAL COMPRESSION ENGINE - EXAMPLE")
    print("=" * 60)
    
    # Try different chunking strategies
    strategies = ["paragraph", "section"]
    
    for strategy in strategies:
        print(f"\n\n{'='*60}")
        print(f"Processing with '{strategy}' chunking strategy...")
        print('='*60)
        
        engine = EnterpriseCompressionEngine(chunk_strategy=strategy)
        
        # Process the document
        result = engine.process(SAMPLE_DOCUMENT)
        
        # Display results
        print(f"\n📊 METADATA")
        print(f"  Total chunks: {result['metadata']['total_chunks']}")
        print(f"  Total extracted items: {result['metadata']['total_extracted_items']}")
        print(f"  Compression ratio: {result['metadata']['compression_ratio']}")
        
        print(f"\n⚡ EXECUTIVE COMPRESSED SUMMARY")
        for idx, item in enumerate(result['executive_compressed_summary'][:5], 1):
            print(f"  {idx}. {item['statement'][:80]}...")
            print(f"     Source: {item['source_chunks']} | Priority: {item['priority']}")
        
        print(f"\n💰 NUMBERS AND LIMITS ({len(result['numbers_and_limits'])} found)")
        for idx, item in enumerate(result['numbers_and_limits'][:5], 1):
            print(f"  {idx}. {item['statement'][:80]}...")
            print(f"     Value: '{item['quote']}' | Source: {item['source_chunks']}")
        
        print(f"\n📅 DATES AND TIMELINES ({len(result['dates_and_timelines'])} found)")
        for idx, item in enumerate(result['dates_and_timelines'][:5], 1):
            print(f"  {idx}. {item['statement'][:80]}...")
            print(f"     Date: '{item['quote']}' | Source: {item['source_chunks']}")
        
        print(f"\n⚠️  EXCEPTIONS AND CONDITIONS ({len(result['exceptions_and_conditions'])} found)")
        for idx, item in enumerate(result['exceptions_and_conditions'][:5], 1):
            print(f"  {idx}. {item['statement'][:80]}...")
            print(f"     Source: {item['source_chunks']}")
        
        print(f"\n🚨 RISKS AND CONSTRAINTS ({len(result['risks_and_constraints'])} found)")
        for idx, item in enumerate(result['risks_and_constraints'][:5], 1):
            print(f"  {idx}. {item['statement'][:80]}...")
            print(f"     Source: {item['source_chunks']}")
        
        print(f"\n❗ CONTRADICTIONS ({len(result['contradictions'])} found)")
        if result['contradictions']:
            for idx, item in enumerate(result['contradictions'][:3], 1):
                print(f"  {idx}. Potential conflict detected:")
                print(f"     Statement 1 ({item['source_chunk_1']}): {item['statement_1'][:60]}...")
                print(f"     Statement 2 ({item['source_chunk_2']}): {item['statement_2'][:60]}...")
        else:
            print("  No contradictions detected")
        
        print(f"\n🔍 TRACEABILITY MAP (sample)")
        for idx, (stmt_id, chunks) in enumerate(list(result['traceability_map'].items())[:5], 1):
            print(f"  {stmt_id} → {chunks}")
        
        # Save to file
        output_file = f"output_{strategy}.json"
        engine.save_output(result, output_file)
        print(f"\n✅ Full output saved to: {output_file}")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
