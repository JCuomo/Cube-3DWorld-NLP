import numpy as np
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from nltk import Tree
from spacy.matcher import Matcher

LABEL = "BLOCK"

sentence0 = "Move the blue block seventeen units south and two units east." #Properly broken down.
sentence1 = "The blue block moves seventeen units south and two units east." #block not identified as subject
sentence2 = "Move the pink block two units up."#up not identified as modifier like east/west/north
sentence10 = "Put the red block on top of the green block."
sentence11 = "Put the red block next to the green block."

nlp = spacy.load('en_core_web_lg')

#Create an nltk object
def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

def on_match_onTopOf(matcher, doc, id, matches):
      print('Callback for on top of')

def on_match_nextTo(matcher, doc, id, matches):
      print('Callback for next to')

#Tokenize and produce tags and visualize what input looks like to parser.
def run_spacy(sentence, verbose=False):
    print("\nRunning spacy tokenizer.")
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

#Get the command from rule based matching by looking for key words
def getRuleBasedCommand(document, verbose=False):
    moves = []
    matcher = Matcher(nlp.vocab)
    matcher.add("on-top-of", on_match_onTopOf, [{"LOWER": "on"}, {"LOWER": "top"}, {"LOWER": "of"}])
    matcher.add("next-to", on_match_nextTo, [{"LOWER": "next"}, {"LOWER": "to"}])

    matches = matcher(document)

    for match_id, start, end in matches:
        span = document[start:end]
        moves.append(span.text)
        if verbose:
            print(span.text)
    return moves

#Get a command from word tags.
def getWordTagCommand(document, verbose=False):
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

def getCommand(document, verbose=False):
    print("\nCommand in sentence: ")
    moves = getRuleBasedCommand(document, True)
    if not moves:
        moves = getWordTagCommand(document, True)
    return moves

def main():

    doc = run_spacy(sentence11, True)

    getSingleBlockFromInput(doc, True)

    getCommand(doc, True)



if __name__ == '__main__':
    main()
    