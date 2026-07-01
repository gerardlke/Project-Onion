from rapidfuzz import fuzz


def find_existing(name: str, aggregated: dict, threshold: int = 85):
    """
    Return name of best matching concept or None using fuzzy string match on lowercased names

    Input:

    Ouput:
    """
    best_match, best_score = None, 0.0
    for existing in aggregated:
        fuzzy_ratio = fuzz.ratio(name.lower(), aggregated[existing]["name"].lower())
        print(name.lower(), aggregated[existing]["name"].lower(), fuzzy_ratio)
        if fuzzy_ratio >= threshold and fuzzy_ratio > best_score:
            best_match = aggregated[existing]["name"]
            best_score = fuzzy_ratio
    return best_match


if __name__ == '__main__':
    find_existing(
        "tree rotation",
        {
            "Binary Search Trees (BSTss)": {"name": "Tree Traversal"},
            "Black White Trees": {"name": "Tree rotation"}
        }
    )

git commit -m "updated logging in model files (encoder, llm, nli) + improved