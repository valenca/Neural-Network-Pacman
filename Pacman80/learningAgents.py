"""
Alterado por
Alexandre Jesus - 2010130268
Gustavo Martins - 2010131414
Joao Valenca - 2010130607
"""

from pacman import Directions
import layout
from game import Agent
from random import choice, random
from util import loadFile, loadFilesFromList, loadFilesUntil, getStateRepresentation
import math

class NeuralNetworkAgent(Agent):

	def __init__(self):
		self.euler = math.e
		self.learningFactor = 0.1
		self.neurons = []
		self.weights = []
		self.nNeurons = range(20,5,-5)
		self.nNeurons.append(5)
		return

	def printNeurons(self):
		for i in range(len(self.neurons)):
			for j in range(len(self.neurons[i])):
				print round(self.neurons[i][j], 3),
			print 

	def sig(self, value):
		return (1.0/(1.0 + self.euler**(-value)))

	def initialization(self):

		#--- Inicializacao de valores de neuronios~---#
		self.neurons.append([])
		for i in self.nNeurons[1:]:
			self.neurons.append([0]*i)
		#

		#--- Inicializacao de pesos [ -0.5 : 0.5 ] ---#
		for i in range(len(self.nNeurons)-1):
			self.weights.append([[random()-0.5 for j in range(self.nNeurons[i+1])] for k in range(self.nNeurons[i])])
		#


	def trainNeuralNetwork(self, case):

		#--- Coloca o input na primeira camada de neuronios ---#
		self.neurons[0] = case[0]
		#

		#--- Criacao de array de erros e valor esperado ---#
		deltas = []
		deltas.append(case[0])
		for i in self.nNeurons[1:]:
			deltas.append([0]*i)
		expected = case[1]
		#

		#--- Calculo de valores de neuronios e output ---#
		for i in range(len(self.nNeurons)-1):
			for j in range(self.nNeurons[i+1]):
				for k in range(self.nNeurons[i]):
					self.neurons[i+1][j] += self.neurons[i][k] * self.weights[i][k][j]
				self.neurons[i+1][j] = self.sig(self.neurons[i+1][j])
		#

		#--- Imprime evolucao da rede neuronal ---#
		#self.printNeurons()
		#print expected
		#print "\n\n"
		#

		#--- Diferenca entra e output esperado e obtido ---#
		for i in range(5):
			deltas[len(self.nNeurons)-1][i] = expected[i] - self.neurons[len(self.nNeurons)-1][i]
		#
		#--- Retropropagacao ---#
		for i in range(len(self.nNeurons)-2, 0, -1):
			for j in range(self.nNeurons[i]):
				for k in range(self.nNeurons[i+1]):
					deltas[i][j] += deltas[i+1][k] * self.weights[i][j][k]
		#

		#--- Recalculo dos pesos ---#
		for i in range(len(self.nNeurons)-1):
			for j in range(self.nNeurons[i]):
				for k in range(self.nNeurons[i+1]):
					self.weights[i][j][k] += self.learningFactor * deltas[i+1][k] * self.neurons[i][j] * (self.neurons[i+1][k] * (1 - self.neurons[i+1][k]))
		#		

	def loadNeuronalNetwork(self):
		import cPickle, os

		#--- Se a rede ja estiver criada, apenas le os dados ---#
		if os.path.isfile("network/network_r_3800_0.1.iia"):
			file = open("network/network_hr_4940_0.1.iia", 'r')
			content = cPickle.load(file)
			self.neurons = content[0]
			self.weights = content[1]
			file.close()
		#
		#--- Caso contrario, cria-a, treina-a e guarda-a em ficheiro ---#
		else:
			#--- Le os ficheiros de treino ---#
			fileNames = []
			c = "Classic"
			for i in ["human", "reactive"]:
				for j in ["contest"+c, "medium"+c, "minimax"+c, "open"+c, "original"+c, "small"+c, "test"+c, "tricky"+c]:
					for k in ["all", "chaser", "guardian", "fearful", "default"]:
						directory = "training/" + i + "/" + j + "/" + k
						if os.path.isdir(directory):
							for l in range(len(os.listdir(directory))):
								fileNames.append(directory + "/training_" + str(l+1) + ".iia")
			#

			#--- Criacao e inicializacao da rede neuronal ---#
			self.initialization()
			#

			#--- Treino da rede neuronal ---#
			files = loadFilesFromList(fileNames)
			for file in files:
				for case in file:
					self.trainNeuralNetwork(case)
			#

			#--- Guarda rede neuronal em ficheiro ---#
			file = open("network/network_hr_4940_0.1.iia", 'w')
			cPickle.dump([self.neurons, self.weights], file) 
			file.close()
			#
	#
		
	def getMove(self, stateRepresentation):

		#--- Coloca o input na primeira camada de neuronios ---#
		self.neurons[0] = stateRepresentation
		#

		#--- Calculo de valores de neuronios e output ---#
		for i in range(len(self.nNeurons)-1):
			for j in range(self.nNeurons[i+1]):
				self.neurons[i+1][j] = 0
				for k in range(self.nNeurons[i]):
					self.neurons[i+1][j] += self.neurons[i][k] * self.weights[i][k][j]
				self.neurons[i+1][j] = self.sig(self.neurons[i+1][j])
		#

		return self.neurons[len(self.nNeurons)-1]

	def getDirection(self, state, actions):
		pacmanPos = state.getPacmanPosition();

		while True:

			randNumber = random() * sum(actions[:-1])

			if(randNumber >= 0 and randNumber < actions[0]):
				if not state.hasWall(pacmanPos[0], pacmanPos[1]+1):
					return Directions.NORTH
			elif(randNumber >= actions[0] and randNumber < sum(actions[0:2])):
				if not state.hasWall(pacmanPos[0], pacmanPos[1]-1):
					return Directions.SOUTH
			elif(randNumber >= sum(actions[0:2]) and randNumber < sum(actions[0:3])):
				if not state.hasWall(pacmanPos[0]+1, pacmanPos[1]):
					return Directions.EAST
			elif(randNumber >= sum(actions[0:3]) and randNumber < sum(actions[0:4])):
				if not state.hasWall(pacmanPos[0]-1, pacmanPos[1]):
					return Directions.WEST


	def getAction(self, state):

		self.loadNeuronalNetwork()

		actions = self.getMove(getStateRepresentation(state))

		#return Directions.NUMBER[actions.index(max(actions))]
		return self.getDirection(state, actions)

		
