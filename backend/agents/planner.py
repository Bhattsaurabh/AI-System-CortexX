from pydantic import BaseModel, Field
from typing import List
from langgraph.graph import StateGraph, END
from typing import TypedDict
import operator

# Define State
class AgentState(TypedDict):
    task: str
    subtasks: List[str]
    current_subtask_index: int
    completed_subtasks: List[str]
    final_output: str

def plan_task(state: AgentState) -> AgentState:
    """Breakdown a task into subtasks."""
    # Placeholder for LLM call
    task = state["task"]
    subtasks = [
        f"Analyze requirements for {task}",
        f"Design architecture for {task}",
        f"Implement {task}"
    ]
    return {"subtasks": subtasks, "current_subtask_index": 0}

def execute_subtask(state: AgentState) -> AgentState:
    """Execute the current subtask."""
    index = state.get("current_subtask_index", 0)
    subtasks = state.get("subtasks", [])
    completed = state.get("completed_subtasks", [])
    
    if index < len(subtasks):
        current_task = subtasks[index]
        print(f"Executing: {current_task}")
        # Placeholder for routing to specific agents based on subtask
        
        completed.append(current_task)
        return {
            "completed_subtasks": completed, 
            "current_subtask_index": index + 1
        }
    return state

def finalize_output(state: AgentState) -> AgentState:
    """Aggregate results into final output."""
    return {"final_output": "All subtasks completed successfully."}

def route_next(state: AgentState) -> str:
    """Determine the next step."""
    if state["current_subtask_index"] < len(state["subtasks"]):
        return "execute"
    return "finalize"

# Define Graph
def create_planner_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("planner", plan_task)
    graph.add_node("executor", execute_subtask)
    graph.add_node("finalizer", finalize_output)
    
    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges("executor", route_next, {
        "execute": "executor",
        "finalize": "finalizer"
    })
    graph.add_edge("finalizer", END)
    
    return graph.compile()
