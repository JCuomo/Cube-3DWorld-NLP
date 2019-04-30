import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from textblob import TextBlob

sentence = "The Blue Block swam over to the Red Block. The Blue Block used to sit on top of the Pink Block known as derpy."


def run_nltk():
    print("Running nltk tokenizer. NNP = Proper Noun, NN = Noun")
    tokens = nltk.word_tokenize(sentence)
    for token in tokens:
        print(token)

    tokens = nltk.pos_tag(tokens)
    print(tokens)

    print()

def run_spacy():
    print("Running spacy tokenizer.")
    nlp = spacy.load('en_core_web_lg')
    document = nlp(sentence)

    for token in document:
        print(token.text)

    for entity in document.ents:
        print(entity.text, entity.label_)
    print()

def run_stanford():
    #nlp = stanfordnlp.Pipeline(processors = "tokenize,pos")

    sentence.sentences[0].print_tokens()

def run_textBlob():
    print("Running textBlob tokenizer.")
    blob = TextBlob(sentence)
    #the tokenizer for textBlob
    print(blob.words)

def main():

    run_nltk()

    run_spacy()

    #run_stanford()

    run_textBlob()


if __name__ == '__main__':
    main()
    