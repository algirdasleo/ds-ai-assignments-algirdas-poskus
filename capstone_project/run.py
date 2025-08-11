import os
from smart_research_assistant import main

project_root = os.path.dirname(os.path.abspath(__file__))

port = os.environ.get("PORT", "8501")

env = os.environ.copy()
env["PYTHONPATH"] = project_root

call = [
    "poetry",
    "run",
    "streamlit",
    "run",
    "--server.port",
    port,
    main.__file__,
]

os.execvpe(call[0], call, env)
