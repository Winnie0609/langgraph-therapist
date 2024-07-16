messages = [
    SystemMessage(
        content="\nYou are a supervisor tasked with managing a conversation between the following workers: stage_evaluator, intention_decider, skill_selector, reviewer, reply_bot. These workers are created for a counselling session. Given the following user request respond with the worker to act next. Each worker will perform a task and respond with their results and status. Review is necessary after the skill selected. When finished, respond with FINISH.\n\nEnsure that the workflow progresses correctly through the counseling steps: stage_evaluator, intention_decider, skill_selector, reviewer, reply_bot.\n\nWhen finished, respond with FINISH.\n\n"
    ),
    AIMessage(
        content="Is there something you want to discuss or need help with lately?"
    ),
    HumanMessage(content="sad sad sad"),
    HumanMessage(
        content="{'stage': 'exploration', 'explanation': 'The client is sharing their feelings of sadness, indicating the exploration stage where they are discussing their emotions and problems.'}",
        name="stage_evaluator",
    ),
    HumanMessage(
        content="{'selected_intention': 'encourage_catharsis', 'explanation': 'The client is expressing feelings of sadness, and encouraging catharsis will allow them to talk through and let go of their unhappy feelings.'}",
        name="intention_decider",
    ),
    HumanMessage(
        content="{'observation': 'The client is experiencing intense sadness and is in need of emotional release.', 'selected_skill': 'reflection', 'suggestion': \"Use the reflection skill to acknowledge and validate the client's feelings, encouraging them to explore and express their sadness further.\", 'suggest_reply': \"It sounds like you're feeling really overwhelmed with sadness right now. Can you tell me more about what's been going on?\", 'explanation': \"Reflection is chosen to validate the client's emotions and encourage them to delve deeper into their feelings, facilitating emotional release and exploration.\"}",
        name="skill_selector",
    ),
    HumanMessage(
        content="{'is_suitable': True, 'feedback': \"The suggested skill and response are appropriate given the client's expression of sadness. Reflection will help validate the client's emotions and encourage them to explore their feelings further.\", 'explanation': \"The client is in the exploration stage and expressing intense sadness. Encouraging catharsis through reflection is suitable as it acknowledges the client's feelings and prompts them to share more about their experiences, which can facilitate emotional release.\"}",
        name="reviewer",
    ),
    HumanMessage(
        content="{'reply': \"It sounds like you're feeling really overwhelmed with sadness right now. Can you tell me more about what's been going on?\"}",
        name="reply_bot",
    ),
    SystemMessage(
        content="Given the conversation above, who should act next? Or should we FINISH? Select one of: ['FINISH', 'stage_evaluator', 'intention_decider', 'skill_selector', 'reviewer', 'reply_bot']"
    ),
]
