import nltk
from nltk.corpus import wordnet
import sys

# Make sure WordNet is available
nltk.download("wordnet", quiet=True)

def simple_paraphrase(sentence):
    """
    Very lightweight paraphraser using WordNet synonyms.
    """
    words = sentence.split()
    new_words = []
    for w in words:
        syns = wordnet.synsets(w)
        if syns:
            lemmas = syns[0].lemmas()
            if lemmas:
                new_words.append(lemmas[0].name().replace("_", " "))
            else:
                new_words.append(w)
        else:
            new_words.append(w)
    return " ".join(new_words)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode: pass paragraph as argument
        text = " ".join(sys.argv[1:])
        print(simple_paraphrase(text))
    else:
        # Interactive mode
        while True:
            text = input("\nEnter a paragraph (or 'quit'): ")
            if text.lower() == "quit":
                break
            print("\n--- Paraphrase ---")
            print(simple_paraphrase(text))
