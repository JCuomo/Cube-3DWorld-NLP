
# coding: utf-8

# In[303]:

import numpy as np
#nltk.download('popular')
#stanfordnlp.download('en')
import spacy
import textacy.extract
from nltk import Tree
from spacy.matcher import Matcher
from dictionaries import *
import sys


from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

LABEL = "BLOCK"

sentence0 = "Move the blue block seventeen units south and two units east." #Properly broken down.
sentence1 = "The blue block moves seventeen units south and two units east." #Same output as above now
sentence2 = "Move the pink block two units up."
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
        return "has location " + commandAndBlock[0][0].text + " " + tup


def getStartingState(document, verbose=False):

    blockStates = []
    sentenceParsed = []
    
    doc = run_spacy(document, verbose)

    sentences = [sent.text for sent in doc.sents]

    commandAndBlock = []

    for sentence in sentences:
        print(sentence)
        subDoc = nlp(sentence)

        b = getSingleBlockFromInput(subDoc, verbose)

        c = getCommand(subDoc, verbose)
        print(b,c)

        commandAndBlock.append([b, c])
        sentenceParsed.append(sentence)

    for item in commandAndBlock:

        bc = convertCommand(item)
        print(bc)

        if verbose:
            print(bc)

        blockStates.append(bc)

    return blockStates,sentenceParsed

def printStateToFile(state, filename):
    with open(filename, 'w') as f:
        for t in state:
            print("(", end='', file=f)
            print(t, end='', file=f)            
            print(")", file=f)






# In[249]:

def getBlocks(st):
    blocks = []
    for t in st:
        for e in t:
            if type(e)!=int and "block" in e:
                blocks.append(e)
    return list(set(blocks))

def getColors(st, block=None):
    # (has block1 location xpos ypos zpos)
    if block:    
        for t in st:
            if ("color" in t) and (block in t):
                return t[3]
        return "undefined"
    else:
        colors = dict()
        for b in getBlocks(st):
            colors[b] = getColors(st, b)
        return colors

def invert_dict(d): 
    inverse = dict() 
    for key,value in d.items(): 
        if value not in inverse: 
            inverse[value] = [key] 
        else: 
            inverse[value].append(key) 
    return inverse

def stateToTuple(st_txt):
    st_t = (tuple(line[1:-1].split(" ")) for line in st_txt)
    return tuple(tuple(int(x) if x.isdigit() else x for x in t) for t in st_t)

def check_color(color):
    colors = ['red','orange','yellow','green','blue','purple','brown','magenta','tan','cyan','olive','maroon','navy','aquamarine','turquoise','silver','lime','teal','indigo','violet','pink','black','white','gray','grey','white','black']
    return color.lower() in colors

def getCoordinates(st, block=None):
    # (has block1 location xpos ypos zpos)    
    if block:    
        coords = []
        for t in st:
            if ("location" in t) and (block in t):
                return t[3:6]
    else:
        coords = dict()
        for b in getBlocks(st):
            coords[b] = getCoordinates(st, b)
        return coords

def getPosOfColor(color_block, block_coord, color):
    d = {}
    try:
        blocks = color_block[color]
    except:
        print("No",color,"blocks")
        return None
    
    for block in blocks:
        d[block_coord[block]] = block
    return d

def getBlocksRelativeLoc(coord_block):
    '''coords should be a list of (x,y,z) and coord_block a dict with coordinate as key and block as value'''
    coords = list(coord_block.keys())

    y_old_M = y_old_m = coords[0][0]
    x_old_M = x_old_m = coords[0][1]
    z_old_M = z_old_m = coords[0][2]

    init = coord_block[coords[0]]

    pos = { 'right' : init, 
            'left'  : init, 
            'top'   : init, 
            'bottom': init, 
            'far'   : init, 
            'close' : init  } 
    
    for c in coords:
        y,x,z = c

        if x > y_old_M:
            x_old = x
            pos['right'] = coord_block[c]
        if x < x_old_m:
            x_old = x
            pos['left'] = coord_block[c]

        if y > y_old_M:
            y_old = y
            pos['far'] = coord_block[c]
        if y < y_old_m:
            y_old = y
            pos['close'] = coord_block[c]

        if z > z_old_M:
            z_old = z
            pos['top'] = coord_block[c]
        if z < z_old_m:
            z_old = z
            pos['bottom'] = coord_block[c]

    return pos

def synonym(in_word):
    
    if in_word in ['right']:
        return 'right'
    
    if in_word in ['left']:
        return 'left'
    
    if in_word in ['top', 'high']:
        return 'top'
    
    if in_word in ['bottom', 'below']:
        return 'bottom'  
    
    if in_word in ['far', 'back']:
        return 'far'
    
    if in_word in ['close', 'front']:
        return 'close'


# In[296]:

def replaceColorByBlock(blockStates, sentenceParsed, start_state):
    
    color_block = invert_dict(getColors(start_state))
    block_coord = getCoordinates(start_state)
    i = -1
    new_blockStates = []
    for state in blockStates:
        i += 1
        for word in state.split():
            if check_color(word):
                if word not in color_block.keys():
                    print("I don't see any",word,"block")
                    continue
                n = len(color_block[word])
                if n==1:
                    block = color_block[word][0]
                    state = state.replace(word, block)
                else:
                    print("Which of the",n,word,"blocks you mean in the phrase",sentenceParsed[i],"?")
                    clarification = input()
                    block = getBlockFromRelativePos(clarification,word)
                    state = state.replace(word, block)
        new_blockStates.append(state)
    return new_blockStates

def interpretatePosition(document, verbose=False):
    if verbose:
        print("\nBlock(s) in sentence:")

    blocks = []
    prevWord = document[0]
    for word in document:
        if (prevWord.dep_ == "det"  and word.dep_ == "pobj") or (prevWord.dep_ == "det"  and word.dep_ == "amod"):
            if verbose:
                print(prevWord, word)
            return str(word)
        
def getBlockFromRelativePos(clarification, color):
    #filter positions to those corresponding to the desire color block
    coord_block = getPosOfColor(color_block, block_coord, color)
    #get blocks according to their semantic position
    blockDistr = getBlocksRelativeLoc(coord_block)
    #interpretate the position the user means
    relativePos = interpretatePosition(nlp(clarification))
    #return the block in that position
    return  blockDistr[synonym(relativePos)]


# In[ ]:

def main(sentence = sentence11):

    try:
        sentence = sys.argv[1]
    except:
        sentence = sentence100

    try:
        outputFile = sys.argv[2]
    except:
        outputFile = "outputParsing"

    print("parsing:",sentence)
    blockStates, sentenceParsed =  getStartingState(sentence, 0)
    printStateToFile(blockStates, outputFile)
    
    startFile = open("start","r")
    start_state = stateToTuple(list(x.rstrip() for x in startFile if x!='\n'))

    replaceColorByBlock(blockStates, sentenceParsed, start_state)



if __name__ == '__main__':
    main()
    

