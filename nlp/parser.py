import numpy as np
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from nltk import Tree
from spacy.matcher import Matcher
from dictionaries import *

LABEL = "BLOCK"

sentence0 = "Move the blue block seventeen units south and two units east." #Properly broken down.
sentence1 = "The blue block moves seventeen units south and two units east." #Same output as above now
sentence2 = "Move the pink block two units up."#up not identified as modifier like east/west/north
sentence10 = "Put the red block on top of the green block."
sentence11 = "Put the red block next to the green block."

sentence100 = "Move the green block three units right. Put the red block next to the green block. Put the blue block on top of the red block."

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

    if verbose:
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

    if verbose:
        print("\nBlock(s) in sentence:")

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
    #matcher.add("on-top-of", on_match_onTopOf, [{"LOWER": "on"}, {"LOWER": "top"}, {"LOWER": "of"}])
    #matcher.add("next-to", on_match_nextTo, [{"LOWER": "next"}, {"LOWER": "to"}])

    matcher.add("on-top-of", None, [{"LOWER": "on"}, {"LOWER": "top"}, {"LOWER": "of"}])
    matcher.add("next-to", None, [{"LOWER": "next"}, {"LOWER": "to"}])

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

    if verbose:
        print("\nCommand in sentence: ")

    moves = getRuleBasedCommand(document, verbose)

    if not moves:
        moves = getWordTagCommand(document, verbose)

    return moves

#Map commands to valid system inputs
def convertCommand(commandAndBlock, verbose=False):

    #Relationals
    if len(commandAndBlock[0]) > 1:
        if "next to" in commandAndBlock[1]:
            return "is " + commandAndBlock[0][0].text + " " + commandAndBlock[0][1].text + " side-by-side"
        elif "on top of" in commandAndBlock[1]:
            return "is " + commandAndBlock[0][0].text + " " + commandAndBlock[0][1].text + " on-top-of"

    #Directionals
    else:
        x = 0
        y = 0
        z = 0
        for direction in commandAndBlock[1]:
            #map right, east to +x
            if "right" in direction or "east" in direction:
                x = textToInt(direction.split(' ', 1)[0])

            #map left, west to -x
            if "left" in direction or "west" in direction:
                x = textToInt(direction.split(' ', 1)[0]) * -1

            #map forward, north to +y
            if "forward" in direction or "north" in direction:
                y = textToInt(direction.split(' ', 1)[0])

            #map backward, south to -y
            if "backward" in direction or "south" in direction:
                y = textToInt(direction.split(' ', 1)[0]) * -1

            #map up to +z
            if "up" in direction:
                z = textToInt(direction.split(' ', 1)[0])

            #map down to -z
            if "down" in direction:
                z = textToInt(direction.split(' ', 1)[0]) * -1

        tup = str(x) + " " + str(y) + " " + str(z)
        return "has " + commandAndBlock[0][0].text + " " + tup


def getStartingState(document, verbose=False):

    blockStates = []

    doc = run_spacy(document, verbose)

    sentences = [sent.text for sent in doc.sents]

    commandAndBlock = []

    for sentence in sentences:

        subDoc = nlp(sentence)

        b = getSingleBlockFromInput(subDoc, verbose)

        c = getCommand(subDoc, verbose)

        commandAndBlock.append([b, c])

    for item in commandAndBlock:

        bc = convertCommand(item)

        if verbose:
            print(bc)

        blockStates.append(bc)

    return blockStates

def main():

    print(getStartingState(sentence100, True))

    

if __name__ == '__main__':
    main()
    