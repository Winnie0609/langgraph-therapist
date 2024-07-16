from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from prompt import (
    supervisor_prompt_template,
    stage_prompt_template,
    intention_prompt_template,
    skill_prompt_template,
    review_prompt_template,
    reply_prompt_template,
)
from model import get_open_ai_model
from intentions import intention_data
from conversation import conversation_example_data


def log_payload_step(state, name):
    print(f"[{name}: log_payload_step]", state)
    print("------------------------------------------------")
    return state


# supervisor agent
members = [
    "stage_evaluator",
    "intention_decider",
    "skill_selector",
    "reviewer",
    "reply_bot",
]
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
                "anyOf": [{"type": "string", "enum": options}],
                "description": "Next step of the agent",
            },
            "explanation": {
                "title": "Explanation",
                "type": "string",
                "description": "Brief explanation of the reason",
            },
        },
        "required": ["next", "explanation"],
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
    # print("[supervisor_chain state]", state)
    # llm = get_open_ai_model(temperature=0, model="gpt-3.5-turbo")
    llm = get_open_ai_model(temperature=0, model="gpt-4o")

    agent = (
        supervisor_prompt
        | (lambda state: log_payload_step(state, "supervisor_chain"))
        | llm.bind_functions(functions=[supervisor_function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
    response = agent.invoke(state)
    print("[supervisor_chain response]", response)
    print("------------------------------------------------")

    return response


# stage agent
def stage_evaluator_node(state):
    # llm = get_open_ai_model(temperature=0, model="gpt-3.5-turbo")
    llm = get_open_ai_model(temperature=0, model="gpt-4o")
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
                    "anyOf": [{"type": "string", "enum": stage_options}],
                    "description": "Stage of the current conversation",
                },
                "explanation": {
                    "title": "Explanation",
                    "type": "string",
                    "description": "Brief explanation of the reason of choosing this stage",
                },
            },
            "required": ["stage", "explanation"],
        },
    }

    stage_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", stage_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(stage_options=", ".join(stage_options))

    agent = (
        stage_prompt
        | (lambda state: log_payload_step(state, "stage_evaluate"))
        | llm.bind_functions(
            functions=[stage_function_def], function_call="evaluate_stage"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[stage_evaluator_node response]", response)
    print("------------------------------------------------")

    return {
        "messages": [HumanMessage(content=str(response), name="stage_evaluator")],
        "current_stage": response["stage"],
    }


# intention agent
def intention_decider_node(state):
    print("[intention_decider_node state]", state)
    print("-------------------------------------------")

    llm = get_open_ai_model(temperature=0.5, model="gpt-4o")
    # llm = get_open_ai_model(temperature=0.5, model="gpt-3.5-turbo")
    current_stage = state["current_stage"]
    intention_list = intention_data[current_stage]
    intention_options = list(intention_list.keys())

    print("[intention_decider_node current_stage]", current_stage)
    print("[intention_decider_node intention_list]", intention_list)
    print("[intention_decider_node intention_options]", intention_options)
    print("-------------------------------------------")

    intention_function_def = {
        "name": "formulate_intention",
        "description": "Decide intention for the therapist to reply user",
        "parameters": {
            "title": "intentionSchema",
            "type": "object",
            "properties": {
                "selected_intention": {
                    "title": "Intention",
                    "anyOf": [{"type": "string", "enum": intention_options}],
                    "description": "Intention of therapist to help client based on conversation",
                },
                "explanation": {
                    "title": "Explanation",
                    "type": "string",
                    "description": "Brief explanation of the reason of choosing this intention",
                },
            },
        },
        "required": ["selected_intention", "explanation"],
    }

    intention_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", intention_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(intention_list=str(intention_list))

    agent = (
        intention_prompt
        | (lambda state: log_payload_step(state, "intention_decider"))
        | llm.bind_functions(
            functions=[intention_function_def], function_call="formulate_intention"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[intention_decider_node response]", response)
    print("------------------------------------------------")

    print("[intention_decider_node selected_intention]", response["selected_intention"])
    print("------------------------------------------------")

    return {
        "messages": [HumanMessage(content=str(response), name="intention_decider")],
        "selected_intention": response["selected_intention"],
    }


# skill selector agent
def skill_selector_node(state):
    llm = get_open_ai_model(temperature=0.5, model="gpt-4o")
    # llm = get_open_ai_model(temperature=0.5, model="gpt-3.5-turbo")

    print("[skill_selector_node state]", state)
    print("******************************************")

    current_stage = state["current_stage"]
    selected_intention = state["selected_intention"]
    is_suitable = state.get("is_suitable")
    ref_conversation = conversation_example_data[current_stage]

    print("[skill_selector_node current_stage]", current_stage)
    print("[skill_selector_node selected_intention]", selected_intention)
    print("[skill_selector_node is_suitable]", is_suitable)
    print("------------------------------------------------")

    if is_suitable is not None and not is_suitable:
        feedback = state["feedback"]
        previous_selections = state["selected_skill"]
        previous_suggestion = state["suggest_reply"]

        previous_answer = (previous_selections, previous_suggestion)
    else:
        feedback = None
        previous_answer = ""

    skill_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", skill_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(
        current_stage=(current_stage),
        selected_intention=(selected_intention),
        ref_conversation=(ref_conversation),
        feedback=(feedback),
        previous_selections=(previous_answer),
    )

    skill_function_def = {
        "name": "select_skill",
        "description": "Choose a skill base on the conversation",
        "parameters": {
            "title": "skillSchema",
            "type": "object",
            "properties": {
                "observation": {
                    "title": "Observation",
                    "type": "string",
                    "description": "Observation of the conversation",
                },
                "selected_skill": {
                    "title": "Selected skill",
                    "type": "string",
                    "description": "Selected skill to meet the intention",
                },
                "suggestion": {
                    "title": "Suggestion",
                    "type": "string",
                    "description": "Suggestion reply to user",
                },
                "suggest_reply": {
                    "title": "Suggestion reply",
                    "type": "string",
                    "description": "Suggestion reply to user",
                },
                "explanation": {
                    "title": "Explanation",
                    "type": "string",
                    "description": "Reason for selection",
                },
            },
            "required": [
                "observations",
                "selected_skill",
                "suggestion",
                "suggest_reply",
                "explanation",
            ],
        },
    }

    agent = (
        skill_prompt
        | (lambda state: log_payload_step(state, "skill_selector"))
        | llm.bind_functions(
            functions=[skill_function_def], function_call="select_skill"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)

    print("[skill_selector_node response]", response)
    print("------------------------------------------------")

    return {
        "messages": [HumanMessage(content=str(response), name="skill_selector")],
        "selected_skill": response["selected_skill"],
        "suggestion": response["suggestion"],
        "suggest_reply": response["suggest_reply"],
    }


# reviewer agent
def reviewer_node(state):
    llm = get_open_ai_model(temperature=0.5, model="gpt-4o")
    # llm = get_open_ai_model(temperature=0.5, model="gpt-3.5-turbo")
    # print("[reply_node state]", state)
    # print("******************************************")

    current_stage = state["current_stage"]
    selected_intention = state["selected_intention"]
    selected_skill = state["selected_skill"]
    suggest_reply = state["suggest_reply"]

    print("[reviewer_node current_stage]", current_stage)
    print("[reviewer_node selected_intention]", selected_intention)
    print("[reviewer_node selected_skill]", selected_skill)
    print("------------------------------------------------")

    reviewer_function_def = {
        "name": "reviewer",
        "description": "Review suggestion based on the conversation",
        "parameters": {
            "title": "reviewSchema",
            "type": "object",
            "properties": {
                "is_suitable": {
                    "title": "Is suitable",
                    "description": "Determine is suggestion appropriate",
                    "type": "boolean",
                },
                "feedback": {
                    "title": "Feedback",
                    "description": "Feedback base on the conversation and suggestion",
                    "type": "string",
                },
                "explanation": {
                    "title": "Explanation",
                    "title": "Feedback base on the conversation and suggestion",
                    "type": "string",
                },
            },
        },
        "required": ["is_suitable", "feedback", "explanation"],
    }

    review_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", review_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(
        current_stage=current_stage,
        selected_intention=selected_intention,
        selected_skill=selected_skill,
        suggest_reply=suggest_reply,
    )

    agent = (
        review_prompt
        | (lambda state: log_payload_step(state, "reviwer"))
        | llm.bind_functions(
            functions=[reviewer_function_def], function_call="reviewer"
        )
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)
    print("[reviewer_node response]", response)
    print("------------------------------------------------")

    return {
        "messages": [HumanMessage(content=str(response), name="reviewer")],
        "is_suitable": response["is_suitable"],
        "feedback": response["feedback"],
    }


# reply agent
def reply_bot_node(state):
    # llm = get_open_ai_model(temperature=0.5, model="gpt-3.5-turbo")
    llm = get_open_ai_model(temperature=1, model="gpt-4o")
    # print("[reply_node state]", state)
    # print("******************************************")

    current_stage = state["current_stage"]
    selected_skill = state["selected_skill"]
    selected_intention = state["selected_intention"]
    suggestion = state["suggestion"]
    suggest_reply = state["suggest_reply"]

    print("[reply_bot_node current_stage]", current_stage)
    print("[reply_bot_node selected_skill]", selected_skill)
    print("[reply_bot_node selected_intention]", selected_intention)
    print("[reply_bot_node suggestion]", suggestion)
    print("[reply_bot_node suggest_reply]", suggest_reply)
    print("------------------------------------------------")

    reply_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", reply_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(
        current_stage=(current_stage),
        selected_skill=(selected_skill),
        selected_intention=(selected_intention),
        suggestion=(suggestion),
        suggest_reply=(suggest_reply),
    )

    reply_function_def = {
        "name": "reply_bot",
        "description": "Reply user based on the expert suggestion",
        "parameters": {
            "title": "skillSchema",
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
        | (lambda state: log_payload_step(state, "reply_bot"))
        | llm.bind_functions(functions=[reply_function_def], function_call="reply_bot")
        | JsonOutputFunctionsParser()
    )

    response = agent.invoke(state)  # 是不是送 conversation 就好？
    # response = agent.invoke(state)  # 是不是送 conversation 就好？
    print("[reply_node response]", response)
    print("------------------------------------------------")

    return {
        "messages": [HumanMessage(content=str(response), name="reply_bot")],
        "reply": response["reply"],
    }
