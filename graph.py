from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import (
    summarize_user_events_node,
    vector_retrieval_node,
    persuasive_narrative_node
)

def build_recommendation_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("synthesize_intent", summarize_user_events_node)
    workflow.add_node("vector_retrieval", vector_retrieval_node)
    workflow.add_node("generate_narrative", persuasive_narrative_node)

    # Build Edges
    workflow.add_edge(START, "synthesize_intent")
    workflow.add_edge("synthesize_intent", "vector_retrieval")
    workflow.add_edge("vector_retrieval", "generate_narrative")
    workflow.add_edge("generate_narrative", END)

    return workflow.compile()

recommendation_agent = build_recommendation_graph()