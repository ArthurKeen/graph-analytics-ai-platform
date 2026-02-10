"""
Test script for custom industry vertical generation.

This script tests the vertical generation with sample business requirements.
"""

import asyncio
from pathlib import Path
from graph_analytics_ai.ai.agents.industry_vertical import IndustryVerticalAgent
from graph_analytics_ai.ai.reporting.custom_verticals import (
    load_custom_vertical,
    register_custom_vertical
)

# Sample business requirements for testing
SAMPLE_REQUIREMENTS = """
# Supply Chain Analytics - Business Requirements

## 1. Domain Overview
**Industry:** Supply Chain & Logistics
**Primary Function:** Optimize supply chain resilience and detect bottlenecks
**Target Users:** Supply chain analysts, procurement managers, operations directors

## 2. Domain Terminology
**Currency:** USD
**Units:** units, pallets, containers, days (lead time)

**Key Terms:**
- Lead Time: Days from purchase order to delivery
- SKU: Stock Keeping Unit (unique product identifier)
- Single Point of Failure: Critical supplier with no alternatives

**Regulations:**
- Import/Export Compliance
- Customs Documentation Requirements

**Thresholds:**
- Critical inventory level: < 7 days on hand
- High concentration risk: > 30% of volume from single supplier
- Excessive lead time: > 45 days

## 3. Graph Structure

### Node Types
- Supplier: Manufacturing suppliers and vendors (500-1000 entities)
- Warehouse: Distribution centers and storage facilities (20-50 entities)
- Product: SKUs and inventory items (10,000+ entities)
- ShipmentRoute: Transportation corridors (100-200 entities)

### Edge Types
- suppliesTo: Supplier → Warehouse supply relationships
- stores: Warehouse → Product inventory relationships
- shipsVia: Warehouse → ShipmentRoute → Warehouse transportation
- dependsOn: Product → Supplier component dependencies

## 4. Key Metrics
- Lead time variance: Standard deviation of delivery times
- Inventory turnover: Sales / Average inventory
- Geographic concentration: % of suppliers in one region
- Supply chain resilience score: Measure of redundancy
- Bottleneck detection: Identification of constrained nodes

## 5. Patterns to Detect

### Critical Patterns
**Single Point of Failure:**
- Description: One supplier provides critical component with no backup
- Indicators: No alternative suppliers, > 20% of production depends on it
- Business Impact: Production halt if supplier fails
- Example: Supplier S-123 sole provider of Component X (40% of products)

**Geographic Concentration:**
- Description: Over-reliance on suppliers from single region
- Indicators: > 50% of suppliers in one country/region
- Business Impact: Regional disruption affects entire supply chain
- Example: 60% of suppliers in Southeast Asia exposed to typhoon risk

### Valuable Patterns
**Diversified Supply:**
- Description: Multiple qualified suppliers per component
- Value: Resilience, negotiating power, risk mitigation
- Example: Component Y has 3 suppliers across 2 continents

## 6. Risk Classification
- CRITICAL: Immediate threat to production (0-4 hours response)
- HIGH: Significant risk requiring attention (24-48 hours)
- MEDIUM: Moderate concern, monitor (1 week)
- LOW: Optimization opportunity (as convenient)

## 7. Example Insights

### Good Example:
Title: Single Point of Failure - Supplier S-123 Critical Dependency

Description: Supplier S-123 is the sole provider of Component X, used in 40% of 
product line (Products P-001 through P-145). No backup suppliers exist. Current 
inventory: 12 days. Lead time: 45 days. Historical reliability: 85%.

Business Impact:
- RISK: Production halt within 12 days if disrupted
- FINANCIAL: $2.4M/week revenue at risk
- IMMEDIATE: Flag for enhanced monitoring, review inventory daily
- SHORT-TERM: Identify 2 backup suppliers within 60 days
- LONG-TERM: Implement multi-sourcing strategy

Confidence: 0.92
Risk Level: CRITICAL
"""


async def test_vertical_generation():
    """Test custom vertical generation."""
    print("=" * 70)
    print("TESTING CUSTOM VERTICAL GENERATION")
    print("=" * 70)
    print()
    
    # Initialize agent
    print("1. Initializing IndustryVerticalAgent...")
    agent = IndustryVerticalAgent()
    print("   ✓ Agent initialized")
    print()
    
    # Generate vertical
    print("2. Generating custom vertical from sample requirements...")
    print()
    
    try:
        vertical = await agent.generate_vertical(
            business_requirements=SAMPLE_REQUIREMENTS,
            graph_name="test_supply_chain"
        )
        print("   ✓ Vertical generated successfully")
        print()
        
        # Display summary
        print("3. Generated Vertical Summary:")
        print(f"   Name: {vertical['metadata']['display_name']}")
        print(f"   Key: {vertical['metadata']['name']}")
        print(f"   Version: {vertical['metadata']['version']}")
        print()
        print(f"   Node Types: {len(vertical['domain_context']['key_entities']['nodes'])}")
        print(f"   Edge Types: {len(vertical['domain_context']['key_entities']['edges'])}")
        print(f"   Key Metrics: {len(vertical['domain_context'].get('key_metrics', []))}")
        print()
        print(f"   Prompt Length: {len(vertical['analysis_prompt'])} characters")
        print(f"   WCC Patterns: {len(vertical['pattern_definitions'].get('wcc', []))}")
        print(f"   PageRank Patterns: {len(vertical['pattern_definitions'].get('pagerank', []))}")
        print()
        
        # Save to test directory
        print("4. Saving to test output...")
        test_output = Path("test_vertical_output")
        test_output.mkdir(exist_ok=True)
        output_file = test_output / "supply_chain_vertical.json"
        
        await agent.save_vertical(vertical, output_file)
        print(f"   ✓ Saved to: {output_file}")
        print()
        
        # Test loading
        print("5. Testing vertical loading...")
        loaded_vertical = load_custom_vertical(test_output.parent)
        if loaded_vertical:
            print("   ✗ Should not have loaded from wrong directory")
        else:
            print("   ✓ Correctly returned None for wrong directory")
        
        # Test registration
        print()
        print("6. Testing vertical registration...")
        industry_key = register_custom_vertical(vertical)
        print(f"   ✓ Registered with key: {industry_key}")
        print()
        
        # Display sample prompt excerpt
        print("7. Sample from Generated Prompt:")
        print("   " + "-" * 66)
        prompt_lines = vertical['analysis_prompt'].split('\n')[:15]
        for line in prompt_lines:
            print(f"   {line[:66]}")
        print("   " + "-" * 66)
        print(f"   ... ({len(vertical['analysis_prompt'])} characters total)")
        print()
        
        print("=" * 70)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        print(f"Generated vertical saved to: {output_file}")
        print("Review the file to see the complete generated prompt and patterns.")
        print()
        
        return 0
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_vertical_generation())
    exit(exit_code)
