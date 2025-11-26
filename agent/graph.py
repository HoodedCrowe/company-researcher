"""LangGraph workflow definition for the research agent."""

from langgraph.graph import StateGraph, END

from agent.nodes import planner_node, researcher_node, synthesizer_node
from agent.state import AgentState


def create_research_graph() -> StateGraph:
    """
    Create and compile the research agent graph.
    
    Flow:
    Planner -> Researcher -> Synthesizer -> END
    
    The graph uses a simple linear flow:
    1. Planner interprets company and generates queries
    2. Researcher executes searches and extracts facts
    3. Synthesizer creates final briefing
    """
    # Create graph with state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Define edges (linear flow)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Compile graph
    return workflow.compile()


def run_research(company_name: str) -> AgentState:
    """
    Run the research agent for a given company.
    
    Args:
        company_name: Name of company to research
        
    Returns:
        Final AgentState with briefing
    """
    graph = create_research_graph()
    
    # Initialize state
    initial_state = AgentState(company_name_raw=company_name)
    
    # Run graph
    final_state = graph.invoke(initial_state)
    
    return AgentState(**final_state)
