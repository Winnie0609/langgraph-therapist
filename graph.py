from langgraph.graph import END, StateGraph, START
from state import AgentState
from model import get_open_ai_model
from tools import (
    members,
    supervisor_chain,
    stage_evaluator_node,
    technique_selector_node,
    reply_bot_node,
    reviewer_node,
)
from sample import sample_output, sample_conversation

llm = get_open_ai_model(temperature=0, model="gpt-4o")

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_chain)
workflow.add_node("stage_evaluator", stage_evaluator_node)
workflow.add_node("technique_selector", technique_selector_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("reply_bot", reply_bot_node)

for member in members:
    workflow.add_edge(member, "supervisor")

conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
workflow.add_edge(START, "supervisor")

graph = workflow.compile()

# r = graph.invoke(
#     {"messages": conversation},
#     {"recursion_limit": 100},
# )
# # print(r)

# for s in graph.stream(
#     # {"messages": messages},
#     {"messages": conversation},
#     {"recursion_limit": 100},
# ):
#     if "__end__" not in s:
# #         print(s)
# #         print("----")


def invoke_agent(conversation):
    # print("----------------------------------")
    # print("[invoke_agent conversation]", conversation)

    response = graph.invoke(
        {"messages": conversation},
        {"recursion_limit": 100},
    )
    # print("**********************************")
    # print("[response]", response)
    return response

    # return sample_output
