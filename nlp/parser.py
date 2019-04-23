import numpy as np
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from nltk import Tree

LABEL = "BLOCK"

sentence0 = "Move the blue block seventeen units south and two units east." #Properly broken down.
sentence1 = "The blue block moves seventeen units south and two units east." #block not identified as subject
sentence2 = "Move the pink block two units up."#up not identified as modifier like east/west/north
sentence10 = "Put the red block on top of the green block."

#Create an nltk object
def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

#Tokenize and produce tags and visualize what input looks like to parser.
def run_spacy(sentence, verbose=False):
    print("\nRunning spacy tokenizer.")
    nlp = spacy.load('en_core_web_lg')
    document = nlp(sentence)

    if verbose:
        print("Dependency (DEP) tags:")
        for word in document:
            print ("%s:%s" % (word,word.dep_))
        print()

        print("Part of speech (POS) tags:")
        for word in document:
            print ("%s:%s" % (word,word.pos_))
        print()

        [to_nltk_tree(sent.root).pretty_print() for sent in document.sents]

    return document

#Get multiple blocks from a sentence
def getMultipleBlocksFromInput(document, verbose=False):
    print("\nBlock in sentence:")

    blocks = []
    prevWord = document[0]
    for word in document:
        if prevWord.dep_ == "amod"  and (word.dep_ == "dobj" or word.dep_ == "nsubj"):
            if verbose:
                print(prevWord, word)

            blocks.append(prevWord)
        prevWord = word
    return blocks

#Get block from a sentence
def getSingleBlockFromInput(document, verbose=False):
    print("\nBlock in sentence:")

    blocks = []
    prevWord = document[0]
    for word in document:
        if prevWord.dep_ == "amod"  and (word.dep_ == "dobj" or word.dep_ == "nsubj" or word.dep_ == "pobj"):
            if verbose:
                print(prevWord, word)

            blocks.append(prevWord)
        prevWord = word
    return blocks

#Get movements/commands from sentence
def getMovementsInput(document, verbose=False):
    print("\nCommand in sentence: ")

    moves = []
    nummod = ""
    advmod = ""
    for word in document:
        if word.dep_ == "nummod":
            nummod = str(word)

        if word.dep_ == "advmod" or word.dep_ == "prt":
            advmod = str(word)

        if nummod != "" and advmod != "":
            move = nummod + " " + advmod
            moves.append(move)
            nummod = ""
            advmod = ""

    if verbose:
        for item in moves:
            print(item)
    return moves

def main():

    doc = run_spacy(sentence10, True)

    getSingleBlockFromInput(doc, True)

    getMovementsInput(doc, True)



if __name__ == '__main__':
    main()
    