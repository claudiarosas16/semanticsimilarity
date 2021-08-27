#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 11:55:51 2021

@author: macbookpro
"""
from nltk.corpus import wordnet as wn
import nltk
import numpy as np
from nltk.tokenize import word_tokenize


class GED:
    
    def __init__(self):
            self.word1 = None  #first word to be compared
            self.word2 = None  # second word to be compared
            self.GED = 0 #Initialize the variable to stored the GED distance
            self.hyp =  'entity.n.01' #Default root noed
            self.path1 = None # path from word1 to hypernym node
            self.path2 = None  # path from word2 to hypernym node
            self.tree1 = None  # graph from path1
            self.tree2 = None  # graph from path1 
            self.matrix = None # result matrix from GED calculation
            self.syn1 = None #synset of word1
            self.syn2 = None #synset of word1
            self.w1_definition = "" #word1 text definition
            self.w2_definition = "" #word2 text definition
            self.path1_to_root = 0 # path from word1 to root node
            self.path2_to_root = 0 # path from word2 to root node
            self.GED1 = 0 # GED distance to root (only for double check)
            self.GED2 = 0 # GED distance to root (only for double check)
    
      
    #Levenstein Distance Calculation
    def distance(self, tree1, tree2):
      d=dict()
      for i in range(len(tree1)+1):
         d[i]=dict()
         d[i][0]=i
      for i in range(len(tree2)+1):
         d[0][i] = i
      for i in range(1, len(tree1)+1):
         for j in range(1, len(tree2)+1):
            d[i][j] = min(d[i][j-1]+1, d[i-1][j]+1, d[i-1][j-1]+(not tree1[i-1] == tree2[j-1]))
      self.matrix = d
      return d[len(tree1)][len(tree2)]
    
    #Build tree or graph
    def getTree(self,path, hyper):
        tree = []
        for node in path:
            if (node != hyper):
                tree.append(node)
            elif (node == hyper):
                tree.append(node)
                break
        return tree
    
    #WordNet Semantics
    def getSemantics(self):
    
        w1 = wn.synset('entity.n.01')
        w2 = wn.synset('entity.n.01')
        w1syns = wn.synsets(self.word1)
        w1syns = [syn for syn in w1syns if syn.pos() in ['a','n'] and (self.word1==syn.name().split('.')[0])]
        w2syns = wn.synsets(self.word2)
        w2syns = [syn for syn in w2syns if syn.pos() in ['a','n'] and (self.word2==syn.name().split('.')[0])]
        
        if (w1syns and w2syns):
        
            #get name and PoS tag
            for syn in w1syns:
                if (self.word1 in syn.name()):
                    for syn2 in w2syns:
                        if syn2 == syn and syn2.name() == 'entity':
                            continue
                        elif syn2.pos() == syn.pos() and (self.word2 in syn2.name()):
                            w1 = syn
                            w2 = syn2
                            break
                        
                        
            #find common hypernyms with all synsets
            hyps = []
            for syn1 in w1syns:
                pair = dict()
                for syn2 in w2syns:
                    if syn2.pos() == syn1.pos():
                        hyper = syn1.lowest_common_hypernyms(syn2)
                        pair = {'syn1':syn1, 'syn2':syn2, 'hyps':hyper}
                        hyps.append(pair)
                    else:
                        continue
            if len(hyps)>0:
                #find shortest path in common hypernym or WSD
                distances = []
                for pair in hyps:
                    if pair['hyps']:
                        for hyp in pair['hyps']:
                            path1 = [path for path in pair['syn1'].hypernym_paths() if hyp in path][0]
                            path2 = [path for path in pair['syn2'].hypernym_paths() if hyp in path][0]
                            pair['path1'] = path1
                            pair['path2'] = path2
                            pair['shp'] = pair['syn1']._shortest_hypernym_paths(pair['syn2'])[hyp] if pair['syn1']._shortest_hypernym_paths(pair['syn2'])[hyp]>0 else 1000
                            pair['hyp'] = hyp
                    else:
                        return self
                    
                shp =  min([i['shp'] for i in hyps])
                chosenone = [i for i in hyps if i['shp'] == shp][0]
                
                self.syn1 = chosenone['syn1']
                self.syn2 = chosenone['syn2']
                self.hyp = chosenone['hyp']
                path1 = chosenone['path1']
                path2 = chosenone['path2']
                self.w1_definition = self.syn1.definition()
                self.w2_definition = self.syn2.definition()
                
                self.path1_to_root = len(path1)
                self.path2_to_root = len(path2)
                
                self.path1 = path1
                self.path2 = path2
                self.tree1 = self.getTree(path1[::-1], self.hyp)
                self.tree2 = self.getTree(path2[::-1], self.hyp)
                
                
                
                self.GED = self.distance(self.tree1, self.tree2)
                self.GED1 = self.distance(self.tree1, [hyp])
                self.GED2 = self.distance(self.tree2, [hyp])
                
                
        return self
        
    def get_GED(self,word1, word2):
        self.word1 = word1
        self.word2 = word2
        return self.getSemantics()
    
