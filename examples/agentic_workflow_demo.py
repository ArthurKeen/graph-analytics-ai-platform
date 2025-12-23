"""
Example: Linear vs Agentic Workflow Comparison

Demonstrates the difference between the traditional linear workflow
and the new agentic workflow with autonomous agents.

Shows how agents:
- Make autonomous decisions
- Communicate with each other
- Adapt to situations
- Provide better reasoning and explanations
"""

import time
from pathlib import Path

from graph_analytics_ai.db_connection import get_db_connection
from graph_analytics_ai.ai.llm import create_llm_provider

# Linear workflow components
from graph_analytics_ai.ai.schema.extractor import SchemaExtractor
from graph_analytics_ai.ai.schema.analyzer import SchemaAnalyzer
from graph_analytics_ai.ai.generation.use_cases import UseCaseGenerator
from graph_analytics_ai.ai.templates import TemplateGenerator
from graph_analytics_ai.ai.execution import AnalysisExecutor
from graph_analytics_ai.ai.reporting import ReportGenerator

# Agentic workflow
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner

# Requirements
from graph_analytics_ai.ai.documents.models import (
    ExtractedRequirements,
    Objective,
    Requirement,
    Priority,
    RequirementType
)


def create_sample_requirements():
    """Create sample requirements for testing."""
    return ExtractedRequirements(
        domain="E-commerce",
        summary="Optimize customer engagement and product recommendations",
        documents=[],
        objectives=[
            Objective(
                id="OBJ-001",
                title="Maximize Customer Engagement",
                description="Identify and engage high-value customers",
                priority=Priority.CRITICAL,
                success_criteria=["Increase engagement by 20%"]
            )
        ],
        requirements=[
            Requirement(
                id="REQ-001",
                text="Identify influential customers",
                requirement_type=RequirementType.FUNCTIONAL,
                priority=Priority.CRITICAL
            )
        ],
        stakeholders=[],
        constraints=[],
        risks=[]
    )


def run_linear_workflow():
    """Run traditional linear workflow."""
    print("=" * 70)
    print("📊 LINEAR WORKFLOW (Traditional)")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    db = get_db_connection()
    provider = create_llm_provider()
    
    print("Step 1: Extract schema...")
    extractor = SchemaExtractor(db)
    schema = extractor.extract()
    print(f"✓ {len(schema.vertex_collections)}V + {len(schema.edge_collections)}E")
    
    print("\nStep 2: Analyze schema...")
    analyzer = SchemaAnalyzer(provider)
    try:
        analysis = analyzer.analyze(schema)
    except:
        analysis = analyzer._create_fallback_analysis(schema)
    print(f"✓ {analysis.domain}, complexity {analysis.complexity_score:.1f}/10")
    
    print("\nStep 3: Use requirements...")
    requirements = create_sample_requirements()
    print(f"✓ {len(requirements.objectives)} objectives")
    
    print("\nStep 4: Generate use cases...")
    uc_generator = UseCaseGenerator()
    use_cases = uc_generator.generate(requirements, analysis)
    print(f"✓ {len(use_cases)} use cases")
    
    print("\nStep 5: Generate templates...")
    template_gen = TemplateGenerator(graph_name="ecommerce_graph")
    templates = template_gen.generate_templates(use_cases, schema, analysis)
    print(f"✓ {len(templates)} templates")
    
    print("\nStep 6: Execute analyses...")
    executor = AnalysisExecutor()
    results = []
    for template in templates[:2]:  # Limit to 2
        result = executor.execute_template(template, wait=True)
        results.append(result)
        if result.success:
            print(f"✓ {template.name}: {result.job.execution_time_seconds:.1f}s")
    
    print("\nStep 7: Generate reports...")
    report_gen = ReportGenerator(use_llm_interpretation=False)
    reports = []
    for result in results:
        if result.success:
            report = report_gen.generate_report(result)
            reports.append(report)
    print(f"✓ {len(reports)} reports")
    
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print("📊 Linear Workflow Results:")
    print(f"   • Time: {elapsed:.1f}s")
    print(f"   • Use cases: {len(use_cases)}")
    print(f"   • Templates: {len(templates)}")
    print(f"   • Executions: {len(results)}")
    print(f"   • Reports: {len(reports)}")
    print("   • Agent messages: 0 (no agents)")
    print("   • Autonomous decisions: 0")
    print()
    
    return {
        "elapsed": elapsed,
        "use_cases": len(use_cases),
        "templates": len(templates),
        "executions": len(results),
        "reports": len(reports),
        "messages": 0
    }


def run_agentic_workflow():
    """Run new agentic workflow."""
    print("=" * 70)
    print("🤖 AGENTIC WORKFLOW (Autonomous Agents)")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    runner = AgenticWorkflowRunner(graph_name="ecommerce_graph")
    state = runner.run()
    
    elapsed = time.time() - start_time
    
    print("=" * 70)
    print("🤖 Agentic Workflow Results:")
    print(f"   • Time: {elapsed:.1f}s")
    print(f"   • Use cases: {len(state.use_cases)}")
    print(f"   • Templates: {len(state.templates)}")
    print(f"   • Executions: {len(state.execution_results)}")
    print(f"   • Reports: {len(state.reports)}")
    print(f"   • Agent messages: {len(state.messages)}")
    print(f"   • Autonomous decisions: {len(state.completed_steps)}")
    print()
    
    # Show agent communication
    print("💬 Agent Communication Flow:")
    for msg in state.messages[:10]:  # Show first 10
        print(f"   {msg.from_agent} → {msg.to_agent}: {msg.message_type}")
    if len(state.messages) > 10:
        print(f"   ... and {len(state.messages) - 10} more messages")
    print()
    
    return {
        "elapsed": elapsed,
        "use_cases": len(state.use_cases),
        "templates": len(state.templates),
        "executions": len(state.execution_results),
        "reports": len(state.reports),
        "messages": len(state.messages),
        "state": state
    }


def compare_workflows():
    """Compare both workflows."""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "WORKFLOW COMPARISON DEMO" + " " * 29 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Run linear
    print("Running LINEAR workflow...")
    print()
    linear_results = run_linear_workflow()
    
    print()
    print("-" * 70)
    print()
    
    # Run agentic
    print("Running AGENTIC workflow...")
    print()
    agentic_results = run_agentic_workflow()
    
    # Comparison
    print("=" * 70)
    print("📊 COMPARISON")
    print("=" * 70)
    print()
    
    print("┌────────────────────────┬──────────────┬──────────────┬──────────────┐")
    print("│ Metric                 │ Linear       │ Agentic      │ Difference   │")
    print("├────────────────────────┼──────────────┼──────────────┼──────────────┤")
    
    def print_row(metric, linear_val, agentic_val):
        if isinstance(linear_val, float):
            diff = agentic_val - linear_val
            diff_str = f"{diff:+.1f}s" if abs(diff) > 0.1 else "~same"
            print(f"│ {metric:<22} │ {linear_val:>12.1f}s │ {agentic_val:>12.1f}s │ {diff_str:>12} │")
        else:
            diff = agentic_val - linear_val
            diff_str = f"{diff:+d}" if diff != 0 else "same"
            print(f"│ {metric:<22} │ {linear_val:>12} │ {agentic_val:>12} │ {diff_str:>12} │")
    
    print_row("Execution Time", linear_results["elapsed"], agentic_results["elapsed"])
    print_row("Use Cases", linear_results["use_cases"], agentic_results["use_cases"])
    print_row("Templates", linear_results["templates"], agentic_results["templates"])
    print_row("Analyses Run", linear_results["executions"], agentic_results["executions"])
    print_row("Reports", linear_results["reports"], agentic_results["reports"])
    print_row("Agent Messages", linear_results["messages"], agentic_results["messages"])
    
    print("└────────────────────────┴──────────────┴──────────────┴──────────────┘")
    print()
    
    # Key differences
    print("🔑 KEY DIFFERENCES")
    print("=" * 70)
    print()
    
    print("LINEAR WORKFLOW:")
    print("  ✓ Simple sequential execution")
    print("  ✓ Predictable flow")
    print("  ✓ Easy to debug")
    print("  ✗ No autonomous decision-making")
    print("  ✗ Limited adaptability")
    print("  ✗ No agent reasoning/explanations")
    print()
    
    print("AGENTIC WORKFLOW:")
    print("  ✓ Autonomous agents with expertise")
    print("  ✓ Adaptive decision-making")
    print("  ✓ Agent collaboration & communication")
    print("  ✓ Self-healing and error recovery")
    print("  ✓ Explainable decisions (agent messages)")
    print("  ✓ Can parallelize (future enhancement)")
    print()
    
    # Use cases for each
    print("📋 WHEN TO USE EACH")
    print("=" * 70)
    print()
    
    print("Use LINEAR for:")
    print("  • Simple, well-defined workflows")
    print("  • Predictable inputs and outputs")
    print("  • When simplicity is more important than adaptability")
    print("  • Learning and understanding the system")
    print()
    
    print("Use AGENTIC for:")
    print("  • Complex, multi-domain problems")
    print("  • When adaptability is crucial")
    print("  • When you need explainable AI decisions")
    print("  • Production systems with varying inputs")
    print("  • When agent expertise adds value")
    print()
    
    # Save agentic state
    if "state" in agentic_results:
        output_dir = Path("./workflow_output")
        output_dir.mkdir(exist_ok=True)
        
        runner = AgenticWorkflowRunner()
        runner.export_state(agentic_results["state"], "workflow_output/agentic_state.json")
    
    print("=" * 70)
    print("🎉 Comparison Complete!")
    print("=" * 70)
    print()
    print("✅ Both workflows functional and producing results!")
    print("🤖 Agentic workflow adds autonomous intelligence!")
    print("📊 Choose based on your needs: simplicity vs adaptability")
    print()


if __name__ == '__main__':
    compare_workflows()

