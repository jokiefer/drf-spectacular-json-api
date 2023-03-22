def build_json_api_data_frame(schema):
    return {
        "type": "object",
        "properties": {
            "data": schema
        },
        "required": ["data"]
    }
