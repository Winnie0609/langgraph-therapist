from pathlib import Path
import json
from model import get_open_ai_model
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import  HumanMessage
from prompt import (
    supervisor_prompt_template,
    stage_prompt_template,
    technique_prompt_template,
    reply_prompt_template,
    review_prompt_template,
)
from techniques import techniques_data
from typing import Dict


def log_payload_step(state):
    print(f"[log_payload_step]", state)
    return state


script_dir = Path(__file__).parent
file_path = script_dir / "techniques.json"
technique_data = json.loads(file_path.read_text())

llm = get_open_ai_model(temperature=0.5, model="gpt-4o")
# llm = get_open_ai_model(temperature=0, model="gpt-3.5-turbo")

# supervisor agent
members = ["stage_evaluator", "technique_selector", "reviewer", "reply_bot"]
options = ["FINISH"] + members

supervisor_function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": options},
                ],
            }
        },
        "required": ["next"],
    },
}

supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", supervisor_prompt_template),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))


def supervisor_chain(state):
    print("[supervisor_chain state]", state)
    print("------")
    agent = (
        supervisor_prompt
        | log_payload_step
        | llm.bind_functions(functions=[supervisor_function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
    response = agent.invoke(state)
    print("[supervisor_chain response]", response)

    return response


# stage agent
def stage_evaluator_node(state):
    stage_options = ["exploration", "insight", "action"]

    stage_function_def = {
        "name": "evaluate_stage",
        "description": "Evaluate the stage of the conversation",
        "parameters": {
            "title": "stageSchema",
            "type": "object",
            "properties": {
                "stage": {
                    "title": "Stage",
                    "anyOf": [
                        {"enum": stage_options},
                    ],
                }
            },
            "required": ["stage"],
        },
    }

    stage_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", stage_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    agent = (
        stage_prompt
        | log_payload_step
        | llm.bind_functions(
            functions=[stage_function_def], function_call="evaluate_stage"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[stage_evaluator_node response]", response)

    return {
        "messages": [HumanMessage(content=str(response), name="stage_evaluator")],
        "current_stage": response["stage"],
    }


# stage agent
def technique_selector_node(state):
    print("[technique_selector_node state]", state)
    print("******************************************")

    current_stage = state["current_stage"]
    print("[technique_selector_node current_stage]", current_stage)
    print("******************************************")

    techniques_options = [item["name"] for item in techniques_data[current_stage]]

    print("[technique_selector_node techniques_options]", techniques_options)
    print("******************************************")

    techniques_detail = techniques_data[current_stage]

    # print("[technique_selector_node techniques_detail]", techniques_detail)
    print("******************************************")

    is_suitable = state.get("is_suitable")

    if is_suitable is not None and not is_suitable:
        feedback = state["feedback"]
        previous_selections = state["selected_technique"]
        previous_suggestion = state["suggestion_reply"]

        previous_answer = (previous_selections, previous_suggestion)
    else:
        feedback = None
        previous_answer = ""

    technique_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", technique_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(
        techniques=str(techniques_detail),
        current_stage=(current_stage),
        feedback=(feedback),
        previous_selections=(previous_answer),
    )

    technique_function_def = {
        "name": "select_technique",
        "description": "Choose a technique base on the conversation",
        "parameters": {
            "title": "techniqueSchema",
            "type": "object",
            "properties": {
                "observation": {
                    "title": "Observation of the conversation",
                    "type": "string",
                    # description
                },
                "selected_technique": {
                    "title": "selected_technique",
                    "anyOf": [{"type": "string", "enum": techniques_options}],
                },
                "suggestion": {"title": "suggestion", "type": "string"},
                "suggestion_reply": {
                    "title": "Suggestion reply to user",
                    "type": "string",
                },
                "reason_for_selection": {
                    "title": "Reason for selection",
                    "type": "string",
                },
            },
            "required": [
                "observations",
                "selected_technique",
                "suggestion",
                "suggestion_reply",
                "reason_for_selection",
            ],
        },
    }

    agent = (
        technique_prompt
        | log_payload_step
        | llm.bind_functions(
            functions=[technique_function_def], function_call="select_technique"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[technique_selector_node response]", response)

    return {
        "messages": [HumanMessage(content=str(response), name="technique_selector")],
        "selected_technique": response["selected_technique"],
        "suggestion": response["suggestion"],
        "suggestion_reply": response["suggestion_reply"],
    }


# reply agent
def reply_bot_node(state):
    print("[reply_node state]", state)
    print("******************************************")

    current_stage = state["current_stage"]
    selected_technique = state["selected_technique"]
    techniques_detail = techniques_data[current_stage]
    selected_technique_info = next(
        (item for item in techniques_detail if item["name"] == selected_technique),
        None,
    )
    suggestion = state["suggestion"]
    suggestion_reply = state["suggestion_reply"]
    # conversation = [
    #     {
    #         "role": "user",
    #         "content": "My boyfriend got angry and punched a hole in the door. Was it necessary to lose his temper like that? ☹️",
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "You're feeling very confused and worried about your boyfriend's behavior, right? Can you tell me more about what happened? How do you see this situation?",
    #     },
    #     {"role": "user", "content": "Not that much, just find it ridiculous."},
    #     {
    #         "role": "user",
    #         "content": "I went to hang out and drink with my girlfriends over the weekend but forgot to tell my boyfriend. He thinks that if I don't feel well, why would I go out drinking.",
    #     },
    # ]

    reply_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", reply_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(
        # conversation=(conversation),
        current_stage=(current_stage),
        selected_technique=(selected_technique),
        selected_technique_info=(str(selected_technique_info)),
        suggestion=(suggestion),
        suggestion_reply=(suggestion_reply),
    )

    reply_function_def = {
        "name": "reply_bot",
        "description": "Reply user based on the expert suggestion",
        "parameters": {
            "title": "techniqueSchema",
            "type": "object",
            "properties": {
                "reply": {
                    "title": "String that reply user",
                    "type": "string",
                }
            },
        },
        "required": ["reply"],
    }

    agent = (
        reply_prompt
        | log_payload_step
        | llm.bind_functions(functions=[reply_function_def], function_call="reply_bot")
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)  # 是不是送 conversation 就好？
    print("[reply_node response]", response)

    return {
        "messages": [HumanMessage(content=str(response), name="reply_bot")],
        "reply": response["reply"],
    }


def reviewer_node(state):
    print("[reply_node state]", state)
    print("******************************************")

    reviewer_function_def = {
        "name": "reviewer",
        "description": "Review suggestion based on the conversation",
        "parameters": {
            "title": "reviewSchema",
            "type": "object",
            "properties": {
                "is_suitable": {
                    "title": "Determine is suggestion appropriate",
                    "type": "boolean",
                },
                "feedback": {
                    "title": "Feedback base on the conversation and suggestion",
                    "type": "string",
                },
            },
        },
        "required": ["is_suitable", "feedback"],
    }

    review_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", review_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    agent = (
        review_prompt
        | log_payload_step
        | llm.bind_functions(
            functions=[reviewer_function_def], function_call="reviewer"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[stage_evaluator_node response]", response)

    return {
        "messages": [HumanMessage(content=str(response), name="reviewer")],
        "is_suitable": response["is_suitable"],
        "feedback": response["feedback"],
    }
