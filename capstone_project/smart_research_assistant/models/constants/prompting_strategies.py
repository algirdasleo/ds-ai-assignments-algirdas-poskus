PROMPT_STRATEGIES = {
    "Zero-shot Prompt": ("Explain the concept of gravity to a five-year-old."),
    "One-shot Prompt": (
        "Example:\n"
        "Topic: Electricity\n"
        "Explanation: Imagine electricity like invisible energy that runs through wires like water in a hose. It helps lights turn on and keeps the fridge cold.\n\n"
        "Now explain this:\n"
        "Topic: Gravity\n"
        "Explanation:"
    ),
    "Few-shot Prompt": (
        "Examples:\n"
        "Topic: Electricity\n"
        "Explanation: Imagine electricity like invisible energy that runs through wires like water in a hose. It helps lights turn on and keeps the fridge cold.\n\n"
        "Topic: The Internet\n"
        "Explanation: The internet is like a magic library where you can ask questions and get answers right away, using a computer or phone.\n\n"
        "Topic: Gravity\n"
        "Explanation:"
    ),
    "Chain of Thought Prompt": (
        "Q: How can you explain something complex to a five-year-old using step-by-step thinking?\n"
        "A: Start by picking something they've likely seen before. Let's use electricity as an example.\n"
        "Next, use a simple comparison: 'Electricity is like invisible energy that moves through wires, kind of like water moving through a hose.'\n"
        "Then, connect it to something familiar: 'It helps turn on the lights and makes your toys work when you plug them in.'\n"
        "Finally, ask a fun question to keep them curious: 'Can you think of something in your room that uses electricity?'\n"
        "Okay, now that we've done electricity...\n\n"
        "Can you explain gravity to me like I am a five year-old?\n"
    ),
    "Role-based Prompt (System Prompt)": ("Explain the concept of gravity to a five-year-old."),
}
