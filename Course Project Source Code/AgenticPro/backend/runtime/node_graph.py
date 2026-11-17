
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class GraphState:
    """Stores data shared between nodes in the workflow."""

    submission_id: str
    status: str = "queued"
    current_node: str | None = "start"
    outputs: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    approval_required: bool = False
    approved: bool = False


@dataclass
class GraphNode:
    """Represents one stage in the node graph."""

    name: str
    action: Callable[[GraphState], GraphState]
    next_node: str | None = None
    router: Callable[[GraphState], str | None] | None = None


class NodeGraph:
    """Executes sequential, conditional, and parallel workflow nodes."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}

    def add_node(self, node: GraphNode) -> None:
        """Register a node in the graph."""

        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists.")

        self.nodes[node.name] = node

    def run(self, start_node: str, state: GraphState) -> GraphState:
        """Run nodes until completion, an error, or an approval pause."""

        if start_node not in self.nodes:
            raise ValueError(f"Start node '{start_node}' does not exist.")

        state.current_node = start_node
        state.status = "running"

        while state.current_node is not None:
            node = self.nodes.get(state.current_node)

            if node is None:
                state.errors.append(
                    f"Node '{state.current_node}' does not exist."
                )
                state.status = "error"
                break

            try:
                updated_state = node.action(state)

                if not isinstance(updated_state, GraphState):
                    raise TypeError(
                        f"Node '{node.name}' must return a GraphState."
                    )

                state = updated_state

            except Exception as error:
                state.errors.append(f"Node '{node.name}' failed: {error}")
                state.status = "error"
                break

            if state.status == "error":
                break

            # Pause if a human approval is required.
            if state.approval_required and not state.approved:
                state.status = "waiting_for_approval"
                state.current_node = node.name
                break

            try:
                # Choose the next node using conditional routing or a fixed link.
                if node.router is not None:
                    next_node = node.router(state)
                else:
                    next_node = node.next_node

            except Exception as error:
                state.errors.append(
                    f"Routing from node '{node.name}' failed: {error}"
                )
                state.status = "error"
                break

            # Validate the destination before moving to it.
            if next_node is not None and next_node not in self.nodes:
                state.errors.append(
                    f"Next node '{next_node}' does not exist."
                )
                state.status = "error"
                break

            state.current_node = next_node

        if state.status == "running":
            state.status = "completed"

        return state

    def run_parallel(
        self,
        node_names: list[str],
        state: GraphState,
        max_workers: int | None = None,
    ) -> GraphState:
        """
        Run independent nodes concurrently.

        Each node receives its own copy of the input state.
        Outputs are merged into the original state after execution.

        Each parallel node should write to distinct output keys.
        """

        if not node_names:
            state.errors.append("No nodes were provided for parallel execution.")
            state.status = "error"
            return state

        if len(set(node_names)) != len(node_names):
            state.errors.append(
                "Duplicate node names are not allowed in parallel execution."
            )
            state.status = "error"
            return state

        missing_nodes = [
            name for name in node_names if name not in self.nodes
        ]

        if missing_nodes:
            state.errors.append(
                f"Parallel nodes do not exist: {', '.join(missing_nodes)}"
            )
            state.status = "error"
            return state

        state.status = "running"
        parallel_results: dict[str, GraphState] = {}
        parallel_errors: list[str] = []

        def execute_node(node_name: str) -> tuple[str, GraphState]:
            """Execute a node against an isolated copy of the shared state."""

            node = self.nodes[node_name]

            branch_state = GraphState(
                submission_id=state.submission_id,
                status="running",
                current_node=node_name,
                outputs=dict(state.outputs),
                errors=list(state.errors),
                approval_required=state.approval_required,
                approved=state.approved,
            )

            result_state = node.action(branch_state)

            if not isinstance(result_state, GraphState):
                raise TypeError(
                    f"Node '{node_name}' must return a GraphState."
                )

            return node_name, result_state

        worker_count = max_workers or len(node_names)

        try:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = {
                    executor.submit(execute_node, name): name
                    for name in node_names
                }

                for future in as_completed(futures):
                    node_name = futures[future]

                    try:
                        result_name, result_state = future.result()
                        parallel_results[result_name] = result_state

                    except Exception as error:
                        parallel_errors.append(
                            f"Parallel node '{node_name}' failed: {error}"
                        )

        except Exception as error:
            parallel_errors.append(
                f"Parallel execution failed: {error}"
            )

        # Stop if any branch failed.
        if parallel_errors:
            state.errors.extend(parallel_errors)
            state.status = "error"
            return state

        # Merge outputs in the requested node order for predictable behavior.
        for node_name in node_names:
            branch_state = parallel_results[node_name]

            if branch_state.status == "error":
                state.errors.extend(branch_state.errors)
                state.errors.append(
                    f"Parallel node '{node_name}' reported an error."
                )
                state.status = "error"
                return state

            new_keys = set(branch_state.outputs) - set(state.outputs)

            # Existing output keys must not be silently overwritten.
            conflicting_keys = {
                key
                for key in new_keys
                if key in state.outputs
            }

            if conflicting_keys:
                state.errors.append(
                    f"Output conflict in node '{node_name}'."
                )
                state.status = "error"
                return state

            state.outputs.update(
                {
                    key: branch_state.outputs[key]
                    for key in new_keys
                }
            )

            state.errors.extend(
                error
                for error in branch_state.errors
                if error not in state.errors
            )

            if branch_state.approval_required:
                state.approval_required = True

            if branch_state.approved:
                state.approved = True

        if state.approval_required and not state.approved:
            state.status = "waiting_for_approval"
        else:
            state.status = "completed"

        state.current_node = None
        return state
