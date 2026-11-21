import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from backend.runtime.node_graph import NodeGraph, GraphNode, GraphState

def test_node_graph_sequential_execution():
    graph = NodeGraph()

    def step1(state: GraphState) -> GraphState:
        state.outputs["parsed"] = True
        return state

    def step2(state: GraphState) -> GraphState:
        state.outputs["executed"] = True
        return state

    graph.add_node(GraphNode(name="parse", action=step1, next_node="execute"))
    graph.add_node(GraphNode(name="execute", action=step2, next_node=None))

    initial_state = GraphState(submission_id="sub-test-001", status="queued")
    final_state = graph.run(start_node="parse", state=initial_state)

    assert final_state.status == "completed"
    assert final_state.outputs["parsed"] is True
    assert final_state.outputs["executed"] is True

def test_node_graph_conditional_routing():
    graph = NodeGraph()

    def check_security(state: GraphState) -> GraphState:
        # Check if malicious
        if state.outputs.get("has_taint", False):
            state.outputs["quarantined"] = True
        return state

    def route_security(state: GraphState) -> str:
        if state.outputs.get("quarantined", False):
            return "quarantine"
        return "sandbox"

    def sandbox_exec(state: GraphState) -> GraphState:
        state.outputs["sandbox_passed"] = True
        return state

    def quarantine_handler(state: GraphState) -> GraphState:
        state.outputs["blocked"] = True
        state.status = "quarantined"
        return state

    graph.add_node(GraphNode(name="security", action=check_security, router=route_security))
    graph.add_node(GraphNode(name="sandbox", action=sandbox_exec, next_node=None))
    graph.add_node(GraphNode(name="quarantine", action=quarantine_handler, next_node=None))

    # Test clean flow
    clean_state = GraphState(submission_id="sub-clean", outputs={"has_taint": False})
    res_clean = graph.run("security", clean_state)
    assert res_clean.outputs.get("sandbox_passed") is True
    assert "blocked" not in res_clean.outputs

    # Test tainted flow
    taint_state = GraphState(submission_id="sub-taint", outputs={"has_taint": True})
    res_taint = graph.run("security", taint_state)
    assert res_taint.outputs.get("blocked") is True
    assert "sandbox_passed" not in res_taint.outputs

def test_node_graph_parallel_execution():
    graph = NodeGraph()

    def task_a(state: GraphState) -> GraphState:
        state.outputs["metric_a"] = 10
        return state

    def task_b(state: GraphState) -> GraphState:
        state.outputs["metric_b"] = 20
        return state

    graph.add_node(GraphNode(name="node_a", action=task_a))
    graph.add_node(GraphNode(name="node_b", action=task_b))

    init_state = GraphState(submission_id="sub-parallel")
    result = graph.run_parallel(["node_a", "node_b"], init_state)

    assert result.status == "completed"
    assert result.outputs["metric_a"] == 10
    assert result.outputs["metric_b"] == 20
