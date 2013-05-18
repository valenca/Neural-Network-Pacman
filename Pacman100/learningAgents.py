from game import Agent
from random import choice
from util import loadFile, loadFilesFromList, loadFilesUntil

class NeuralNetworkAgent(Agent):
  
    def __init__(self):
        pass
        
    def trainNeuralNetwork(self, case):
        pass
      
    def getAction(self, state):
        return choice(state.getLegalPacmanActions());

        