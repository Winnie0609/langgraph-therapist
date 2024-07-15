from langchain_core.messages import HumanMessage

sample_conversation = [
    {
        "role": "assistant",
        "content": "Is there something you want to discuss or need help with lately?",
    },
    {
        "role": "user",
        "content": "My boyfriend got angry and punched a hole in the door. Was it necessary to lose his temper like that? ☹️",
    },
    {
        "role": "assistant",
        "content": "You're feeling very confused and worried about your boyfriend's behavior, right? Can you tell me more about what happened? How do you see this situation?",
    },
    {"role": "user", "content": "Not that much, just find it ridiculous."},
    {
        "role": "user",
        "content": "I went to hang out and drink with my girlfriends over the weekend but forgot to tell my boyfriend. He thinks that if I don't feel well, why would I go out drinking.",
    },
    {
        "role": "user",
        "content": "Please give me some approach to fell better right now.",
    },
    {
        "role": "user",
        "content": "Then he started to criticize me, saying I made a mistake and need to be punished. He said he wouldn't take me to the gym and would cancel plans with our friend xx.",
    },
    {
        "role": "user",
        "content": "While talking about this, he got furious and punched the door.",
    },
    {
        "role": "user",
        "content": "Is this really that serious? I just didn't inform him, and now he wants me to pay for the door repair. It's unbelievable.",
    },
]

sample_output = {
    "messages": [
        {
            "role": "assistant",
            "content": "You're feeling very confused and worried about your boyfriend's behavior, right? Can you tell me more about what happened? How do you see this situation?",
        },
        {"role": "user", "content": "Not that much, just find it ridiculous."},
        {
            "role": "user",
            "content": "I went to hang out and drink with my girlfriends over the weekend but forgot to tell my boyfriend. He thinks that if I don't feel well, why would I go out drinking.",
        },
        {
            "role": "user",
            "content": "Please give me some approach to fell better right now.",
        },
        HumanMessage(content="{'stage': 'action'}", name="stage_evaluator"),
        HumanMessage(
            content="{'observation': 'The user is seeking immediate relief from their emotional distress.', 'selected_technique': 'direct_guidance', 'suggestion': 'Use a relaxation technique to help the user feel better immediately.', 'suggestion_reply': \"Let's try a quick relaxation exercise. Take a deep breath in through your nose for a count of four, hold it for a count of four, and then slowly exhale through your mouth for a count of four. Repeat this a few times and see if it helps you feel more calm.\", 'reason_for_selection': 'The user is asking for immediate ways to feel better, which is best addressed through direct guidance with a relaxation technique.'}",
            name="technique_selector",
        ),
        HumanMessage(
            content="{'is_suitable': True, 'feedback': \"The suggestion to use a relaxation technique is appropriate given the user's request for immediate relief. Direct guidance with a specific exercise is a practical and effective way to help them manage their emotional distress in the moment.\", 'reason_for_feedback': \"The user is seeking immediate ways to feel better, and a relaxation technique is a well-established method to quickly reduce stress and anxiety. The therapist's suggestion is clear, actionable, and directly addresses the user's need.\"}",
            name="reviewer",
        ),
        HumanMessage(
            content="{'reply': \"Let's try a quick relaxation exercise. Take a deep breath in through your nose for a count of four, hold it for a count of four, and then slowly exhale through your mouth for a count of four. Repeat this a few times and see if it helps you feel more calm.\"}",
            name="reply_bot",
        ),
    ],
    "next": "FINISH",
    "current_stage": "action",
    "selected_technique": "direct_guidance",
    "suggestion": "Use a relaxation technique to help the user feel better immediately.",
    "suggestion_reply": "Let's try a quick relaxation exercise. Take a deep breath in through your nose for a count of four, hold it for a count of four, and then slowly exhale through your mouth for a count of four. Repeat this a few times and see if it helps you feel more calm.",
    "is_suitable": True,
    "feedback": "The suggestion to use a relaxation technique is appropriate given the user's request for immediate relief. Direct guidance with a specific exercise is a practical and effective way to help them manage their emotional distress in the moment.",
    "reply": "Let's try a quick relaxation exercise. Take a deep breath in through your nose for a count of four, hold it for a count of four, and then slowly exhale through your mouth for a count of four. Repeat this a few times and see if it helps you feel more calm.",
}
