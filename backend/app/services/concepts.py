import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from app.schemas.upload import ExtractedConcept


STOPWORDS = set(ENGLISH_STOP_WORDS)


def extract_concepts(chunks):
    """Extracts main concept from text across chunks

    Input:

    Ouput:
    """

    extracted_concepts = []

    # Iterate through chunks
    for index, chunk in enumerate(chunks):
        
        # Tokenize each chunk
        words = tokenize(chunk)

        # Find concepts in text chunks
        filtered_words = [
            word for word in words
            if word not in STOPWORDS and len(word) > 2
        ]
        word_counts = Counter(filtered_words)
        top_concepts = word_counts.most_common(10)

        # Append concept
        for word, frequency in top_concepts:
            extracted_concepts.append(
                ExtractedConcept(
                    concept=word,
                    frequency=frequency,
                    chunk_index=index
                )
            )

    return extracted_concepts


def tokenize(text):
    """Tokenize text

    Input:

    Ouput:
    """
    text = text.lower()
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    # TODO: Use tokenizer maybe idk
    return words