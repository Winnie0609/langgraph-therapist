from langgraph.graph import END, StateGraph, START
from state import AgentState
from tools import (
    members,
    supervisor_chain,
    stage_evaluator_node,
    intention_decider_node,
    skill_selector_node,
    reply_bot_node,
    reviewer_node,
)

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_chain)
workflow.add_node("stage_evaluator", stage_evaluator_node)
workflow.add_node("intention_decider", intention_decider_node)
workflow.add_node("skill_selector", skill_selector_node)
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
    print("[invoke_agent conversation]", conversation)
    print("----------------------------------")

    response = graph.invoke(
        {"messages": conversation},
        {"recursion_limit": 100},
    )
    # print("**********************************")
    # print("[response]", response)
    return response
