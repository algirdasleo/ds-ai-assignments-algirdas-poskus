import random
from typing import Dict, List, Literal

import ollama


def get_ollama_models_details() -> Dict[str, Dict[str, str]]:
    return {
        model.model: {
            "Family": getattr(model.details, "family", "Not provided"),
            "Parameter size": getattr(model.details, "parameter_size", "Not provided"),
            "Quantization level": getattr(model.details, "quantization_level", "Not provided"),
        }
        for model in ollama.list().models
        if model.model
    }


def select_model(sorted_models: Dict[str, List[str]], prompt: str) -> str | None:
    if not sorted_models:
        return list(sorted_models.keys())[0]

    if not all(k in sorted_models for k in ["simple", "powerful"]):
        return None

    classified_prompt = classify_prompt(prompt)

    if classified_prompt == "simple":
        return random.choice(sorted_models["simple"])
    elif classified_prompt == "powerful":
        return random.choice(sorted_models["powerful"])
    return None


def sort_models(models: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
    param_sizes = [parse_param_size(item[1].get("Parameter size", "0")) for item in models.items()]
    avg_size = sum(param_sizes) / len(param_sizes)

    model_categories = {"simple": [], "powerful": []}

    for model in models.items():
        size = parse_param_size(model[1].get("Parameter size", "0"))
        if size < avg_size:
            model_categories["simple"].append(model[0])
        else:
            model_categories["powerful"].append(model[0])

    return model_categories


def parse_param_size(size: str) -> float:
    try:
        if "M" in size:
            return float(size.replace("M", "").strip())
        elif "B" in size:
            return float(size.replace("B", "").strip()) * 1000
        elif "T" in size:
            return float(size.replace("T", "").strip()) * 1000000
        return 0
    except ValueError:
        return 0


def classify_prompt(prompt: str) -> Literal["powerful"] | Literal["simple"]:
    advanced_keywords = [
        "code",
        "optimize",
        "debug",
        "analyze",
        "transform",
        "visualize",
        "generate",
        "summarize",
        "explain",
        "compare",
        "contrast",
        "predict",
        "classify",
        "cluster",
        "think",
        "create",
        "design",
        "plan",
    ]

    if any(keyword in prompt for keyword in advanced_keywords) or len(prompt.split()) > 50:
        return "powerful"
    return "simple"
