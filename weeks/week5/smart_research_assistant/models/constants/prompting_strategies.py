PROMPT_STRATEGIES = {
    "Zero-shot Prompt": ("Translate the following English sentence to French:\n" "'I am very happy to meet you.'"),
    "One-shot Prompt": (
        "Example:\n"
        "English: 'Good morning.'\n"
        "French: 'Bonjour.'\n\n"
        "Now translate:\n"
        "English: 'I am very happy to meet you.'"
    ),
    "Few-Shot Prompt": (
        "Examples:\n"
        "English: 'Good morning.' -> French: 'Bonjour.'\n"
        "English: 'How are you?' -> French: 'Comment ça va ?'\n"
        "English: 'Thank you very much.' -> French: 'Merci beaucoup.'\n\n"
        "Now translate:\n"
        "English: 'I am very happy to meet you.' -> French:"
    ),
    "Chain of Thought Prompt": (
        "Q: If there are 3 red balls and 5 blue balls in a box, and you take out 2 balls without looking, "
        "what is the probability that both are blue?\n"
        "A: First, calculate the total number of ways to choose 2 balls from 8. That's C(8,2) = 28.\n"
        "Next, calculate the number of ways to choose 2 blue balls from 5. That's C(5,2) = 10.\n"
        "So, the probability is 10/28 = 5/14."
    ),
    "Role-based Prompt (System Prompt)": ("User: Translate the following: 'I am very happy to meet you.'"),
}
