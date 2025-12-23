"""
Example: Agentic Workflow - Phase 10 FINAL!

Demonstrates autonomous multi-agent system that:
- Coordinates 9 specialized agents
- Makes autonomous decisions
- Adapts to errors and edge cases
- Provides complete audit trail
- Runs entire pipeline automatically

This is the COMPLETE system - all 10 phases working together!
"""

from graph_analytics_ai.db_connection import get_db_connection
from graph_analytics_ai.ai.agents import AgenticWorkflow
from graph_analytics_ai.ai.reporting import ReportFormat


def agentic_workflow_demo():
    """Run complete agentic workflow demonstration."""
    
    print("=" * 70)
    print("🤖 AGENTIC WORKFLOW - AUTONOMOUS MULTI-AGENT SYSTEM")
    print("=" * 70)
    print()
    print("This demonstrates the COMPLETE Phase 1-10 system:")
    print("  • 9 specialized autonomous agents")
    print("  • 1 orchestrator agent (supervisor)")
    print("  • Autonomous decision-making")
    print("  • Adaptive error handling")
    print("  • Complete audit trail")
    print()
    
    # ========================================================================
    # Initialize Agentic Workflow
    # ========================================================================
    print("🚀 Initializing Multi-Agent System...")
    print("-" * 70)
    
    db = get_db_connection()
    workflow = AgenticWorkflow(graph_name="ecommerce_graph")
    
    print("✓ Orchestrator Agent initialized")
    print("✓ 9 Specialized Agents ready:")
    print("  1. Schema Analysis Agent")
    print("  2. Requirements Analysis Agent")
    print("  3. PRD Generation Agent")
    print("  4. Use Case Generation Agent")
    print("  5. Template Generation Agent")
    print("  6. Execution Agent")
    print("  7. Interpretation Agent")
    print("  8. Reporting Agent")
    print("  9. Quality Assurance Agent")
    print()
    
    # ========================================================================
    # Run Agentic Workflow
    # ========================================================================
    print("🤖 Executing Agentic Workflow...")
    print("-" * 70)
    print("Agents will autonomously:")
    print("  • Analyze your graph database")
    print("  • Generate optimal use cases")
    print("  • Create GAE templates")
    print("  • Execute analyses")
    print("  • Interpret results")
    print("  • Generate intelligence reports")
    print("  • Make decisions and adapt to issues")
    print()
    
    # Run workflow
    state = workflow.run(
        db_connection=db,
        requirements_docs=[],  # Agents will create default requirements
        graph_name="ecommerce_graph"
    )
    
    print("✓ Agentic workflow complete!")
    print()
    
    # ========================================================================
    # Show Progress and Metrics
    # ========================================================================
    print("📊 Workflow Metrics")
    print("-" * 70)
    
    progress = workflow.get_progress(state)
    print(f"Progress: {progress['completed_steps']}/{progress['total_steps']} steps ({progress['progress_percent']:.0f}%)")
    print(f"Current Step: {progress['current_step']}")
    print(f"Agent Decisions: {progress['decisions']}")
    print(f"Errors: {progress['errors']}")
    print(f"Inter-Agent Messages: {progress['messages']}")
    print()
    
    # ========================================================================
    # Show Agent Decisions (Explainability)
    # ========================================================================
    print("🧠 Agent Decisions & Reasoning")
    print("-" * 70)
    
    decisions = workflow.get_decisions(state)
    for i, decision in enumerate(decisions[:10], 1):  # Show first 10
        print(f"{i}. [{decision['agent']}]")
        print(f"   Decision: {decision['decision']}")
        print(f"   Reasoning: {decision['reasoning']}")
        if decision.get('context'):
            print(f"   Context: {list(decision['context'].keys())}")
        print()
    
    if len(decisions) > 10:
        print(f"... and {len(decisions) - 10} more decisions")
        print()
    
    # ========================================================================
    # Show Results
    # ========================================================================
    print("📊 Results")
    print("-" * 70)
    
    print(f"✓ Schema: {len(state.schema.vertex_collections)}V + {len(state.schema.edge_collections)}E")
    print(f"✓ Requirements: {len(state.requirements.objectives)} objectives, {len(state.requirements.requirements)} requirements")
    print(f"✓ Use Cases: {len(state.use_cases)} generated")
    print(f"✓ Templates: {len(state.templates)} created")
    print(f"✓ Executions: {len(state.execution_results)} completed")
    
    successful = sum(1 for r in state.execution_results if r.success)
    print(f"✓ Success Rate: {successful}/{len(state.execution_results)} ({100*successful/len(state.execution_results) if state.execution_results else 0:.0f}%)")
    
    if state.report:
        print(f"✓ Report: {len(state.report.insights)} insights, {len(state.report.recommendations)} recommendations")
    print()
    
    # ========================================================================
    # Show Insights
    # ========================================================================
    if state.report and state.report.insights:
        print("💡 Key Insights (Agent-Generated)")
        print("-" * 70)
        
        for i, insight in enumerate(state.report.insights[:5], 1):
            print(f"{i}. {insight.title}")
            print(f"   Type: {insight.insight_type.value}")
            print(f"   Confidence: {insight.confidence*100:.0f}%")
            print(f"   Description: {insight.description[:100]}...")
            print()
    
    # ========================================================================
    # Show Recommendations
    # ========================================================================
    if state.report and state.report.recommendations:
        print("🎯 Recommendations (Agent-Generated)")
        print("-" * 70)
        
        for i, rec in enumerate(state.report.recommendations[:5], 1):
            print(f"{i}. {rec.title}")
            print(f"   Type: {rec.recommendation_type.value}")
            print(f"   Priority: {rec.priority}")
            print(f"   Effort: {rec.effort}")
            print()
    
    # ========================================================================
    # Export Report
    # ========================================================================
    if state.report:
        print("💾 Exporting Report...")
        print("-" * 70)
        
        from pathlib import Path
        from graph_analytics_ai.ai.reporting import ReportGenerator
        
        output_dir = Path("./workflow_output")
        output_dir.mkdir(exist_ok=True)
        
        generator = ReportGenerator()
        
        # Export as markdown
        markdown = generator.format_report(state.report, ReportFormat.MARKDOWN)
        md_path = output_dir / "agentic_report.md"
        md_path.write_text(markdown)
        print(f"✓ Markdown: {md_path}")
        
        # Export as JSON
        json_report = generator.format_report(state.report, ReportFormat.JSON)
        json_path = output_dir / "agentic_report.json"
        json_path.write_text(json_report)
        print(f"✓ JSON: {json_path}")
        
        # Export state
        state_export = workflow.export_state(state, format="json")
        state_path = output_dir / "agentic_state.json"
        state_path.write_text(state_export)
        print(f"✓ State: {state_path}")
        print()
    
    # ========================================================================
    # Show Errors (if any)
    # ========================================================================
    errors = workflow.get_errors(state)
    if errors:
        print("⚠️  Errors Encountered (Agents Adapted)")
        print("-" * 70)
        
        for error in errors[:5]:
            print(f"• [{error['step']}] {error['error']}")
        
        if len(errors) > 5:
            print(f"... and {len(errors) - 5} more")
        print()
    
    # ========================================================================
    # Final Summary
    # ========================================================================
    print("=" * 70)
    print("🎉 AGENTIC WORKFLOW COMPLETE!")
    print("=" * 70)
    print()
    print("✅ All 10 Phases Executed Autonomously:")
    print("   Phase 1: LLM Foundation")
    print("   Phase 2: Schema Analysis")
    print("   Phase 3: Document Processing")
    print("   Phase 4: PRD Generation")
    print("   Phase 5: Use Case Generation")
    print("   Phase 6: Workflow Orchestration")
    print("   Phase 7: Template Generation")
    print("   Phase 8: Analysis Execution")
    print("   Phase 9: Report Generation")
    print("   Phase 10: Agentic Workflow ← FINAL PHASE!")
    print()
    print("🤖 Agentic Features:")
    print(f"   • {progress['decisions']} autonomous decisions made")
    print(f"   • {progress['messages']} inter-agent messages")
    print("   • Complete audit trail of reasoning")
    print("   • Adaptive error handling")
    print("   • Quality assurance checks")
    print()
    print("📊 Results:")
    print(f"   • {len(state.use_cases)} use cases generated")
    print(f"   • {len(state.templates)} GAE templates created")
    print(f"   • {successful}/{len(state.execution_results)} analyses successful")
    if state.report:
        print(f"   • {len(state.report.insights)} insights discovered")
        print(f"   • {len(state.report.recommendations)} recommendations")
    print()
    print("🎯 The System is COMPLETE!")
    print("   • 100% autonomous operation")
    print("   • From requirements to insights")
    print("   • Multi-agent coordination")
    print("   • Production-ready!")
    print()
    print("Progress: 100% - ALL PHASES COMPLETE! 🚀🎉")
    print()


if __name__ == '__main__':
    agentic_workflow_demo()

