import numpy as np
import nltk
#nltk.download('popular')
import spacy
import textacy.extract

def run_nltk():
    print("Running nltk tokenizer.")
    sentence = "The Blue Block swam over to the Red Block. The Blue Block used to sit on top of the Pink Block known as derpy."
    tokens = nltk.word_tokenize(sentence)
    for token in tokens:
        print(token)
    print()

def run_spacy():
    print("Running spacy tokenizer.")
    nlp = spacy.load('en_core_web_lg')
    sentence = "The Blue Block swam over to the Red Block. The Blue Block used to sit on top of the Pink Block known as derpy."
    document = nlp(sentence)

    for token in document:
        print(token.text)

    for entity in document.ents:
        print(entity.text, entity.label_)
    print()


def main():

    run_nltk()

    run_spacy()

if __name__ == '__main__':
    main()
    