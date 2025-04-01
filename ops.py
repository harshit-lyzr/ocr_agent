import math


TOKEN_ACTION_MAPPING = {
    "gemini": {
        "gemini-1.5-flash": {
            "input_ratio": 0.15,
            "output_ratio": 0.6,
        },
        "gemini-1.5-pro": {
            "input_ratio": 2.5,
            "output_ratio": 10,
        },
        "gemini-2.0-flash": {
            "input_ratio": 0.2,
            "output_ratio": 0.8,
        },
        "gemini-2.0-flash-lite": {
            "input_ratio": 0.15,
            "output_ratio": 0.6,
        },
        "gemini-2.0-flash-exp": {
            "input_ratio": 0.3,
            "output_ratio": 1.2,
        },
    }
}


def calculate_actions(
    llm_provider: str,
    language_model: str,
    num_input_tokens: int,
    num_output_tokens: int,
) -> float:
    provider_mapping = TOKEN_ACTION_MAPPING.get(
        llm_provider.lower(), TOKEN_ACTION_MAPPING[llm_provider]
    )
    model_config = provider_mapping.get(language_model)

    if not model_config:
        return 0.0

    #! Handle dynamic pricing models
    if model_config.get("dynamic_pricing", False):
        pricing_tiers = model_config.get("pricing_tiers", [])

        input_actions = 0
        remaining_input_tokens = num_input_tokens
        tokens_processed = 0

        for tier in pricing_tiers:
            if tier.get("default", False):
                input_ratio = tier.get("input_ratio", 0)
                input_actions += (
                    math.ceil((input_ratio / 2000) * remaining_input_tokens * 100) / 100
                )
                break

            max_tokens = tier.get("max_tokens", 0)
            tokens_in_tier = min(max_tokens - tokens_processed, remaining_input_tokens)

            if tokens_in_tier > 0:
                input_ratio = tier.get("input_ratio", 0)
                input_actions += (
                    math.ceil((input_ratio / 2000) * tokens_in_tier * 100) / 100
                )
                remaining_input_tokens -= tokens_in_tier
                tokens_processed += tokens_in_tier

            if remaining_input_tokens <= 0:
                break

        output_actions = 0
        remaining_output_tokens = num_output_tokens
        tokens_processed = 0

        for tier in pricing_tiers:
            if tier.get("default", False):
                output_ratio = tier.get("output_ratio", 0)
                output_actions += (
                    math.ceil((output_ratio / 2000) * remaining_output_tokens * 100)
                    / 100
                )
                break

            max_tokens = tier.get("max_tokens", 0)
            tokens_in_tier = min(max_tokens - tokens_processed, remaining_output_tokens)

            if tokens_in_tier > 0:
                output_ratio = tier.get("output_ratio", 0)
                output_actions += (
                    math.ceil((output_ratio / 2000) * tokens_in_tier * 100) / 100
                )
                remaining_output_tokens -= tokens_in_tier
                tokens_processed += tokens_in_tier

            if remaining_output_tokens <= 0:
                break

        total_actions = input_actions + output_actions
        return total_actions

    base_cost = model_config.get("base_cost", 0)

    input_ratio = model_config.get("input_ratio", 0)
    output_ratio = model_config.get("output_ratio", 0)

    input_actions = math.ceil((input_ratio / 2000) * num_input_tokens * 100) / 100
    output_actions = math.ceil((output_ratio / 2000) * num_output_tokens * 100) / 100

    total_actions = input_actions + output_actions

    if base_cost > 0:
        total_actions += base_cost

    return total_actions

