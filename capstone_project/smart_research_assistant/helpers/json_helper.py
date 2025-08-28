import ijson


def extract_streamed_json_values(partial_json: str, key: str) -> str:
    try:
        parser = ijson.parse(partial_json.encode())
        for prefix, event, value in parser:
            if prefix == key and event == "string":
                return value
    except Exception:
        pass
    return partial_json
