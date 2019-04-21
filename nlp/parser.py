import numpy as np
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from nltk import Tree

sentence0 = "Move the blue block seventeen units south and two units east."
sentence1 = "The blue block moves seventeen units south and two units east."

sentence1 = "Move the blue block to location B."

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

def run_spacy(verbose=False):
    print("Running spacy tokenizer.")
    nlp = spacy.load('en_core_web_lg')
    document = nlp(sentence0)

    if verbose:
        for word in document:
            print ("%s:%s" % (word,word.dep_))
        print()

        [to_nltk_tree(sent.root).pretty_print() for sent in document.sents]

    return document

def getBlocksFromInput(document, verbose=False):
    print("Running get blocks.")

    blocks = []
    prevWord = document[0]
    for word in document:
        if prevWord.dep_ == "amod" and word.dep_ == "dobj":
            if verbose:
                print()
                print(prevWord, word)
                
            blocks.append(prevWord)
        prevWord = word
    return blocks

def getMovementsInput(document, verbose=False):
    print("Running get moves.")

    moves = []
    nummod = ""
    advmod = ""
    for word in document:
        if word.dep_ == "nummod":
            nummod = str(word)

        if word.dep_ == "advmod":
            advmod = str(word)

        if nummod != "" and advmod != "":
            move = nummod + " " + advmod
            #print(move) 
            moves.append(move)
            nummod = ""
            advmod = ""

    if verbose:
        print()
        for item in moves:
            print(item)
    return moves

def main():

    doc = run_spacy(True)

    getBlocksFromInput(doc, True)

    getMovementsInput(doc, True)



if __name__ == '__main__':
    main()
    