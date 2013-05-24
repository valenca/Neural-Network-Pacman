"""
Alterado por
Alexandre Jesus - 2010130268
Gustavo Martins - 2010131414
Joao Valenca - 2010130607
"""

from pacman import Directions
import layout
from game import Agent
from random import choice, random, shuffle
from util import loadFile, loadFilesFromList, loadFilesUntil, getStateRepresentation
import math

class NeuralNetworkAgent(Agent):

	def __init__(self):
		self.euler = math.e
		self.learningFactor = 0.1
		self.neurons = []
		self.weights = []
		self.biasWeights = []
		self.nNeurons = range(20,5,-5)
		self.nNeurons.append(5)
		self.percTrainingFiles = 0.8
		self.numFiles = 0
		self.numCases = 0
		self.correctCases = 0
		self.stopCondition = 0.0001
		self.lastErrorsSize = 3
		self.lastErrors = [1]*self.lastErrorsSize
		self.lastErrorsIndex = 0
		self.totalError = 0
		self.averageTotalError = 0
		self.minTrainingError = 2.5
		self.averageTrainingError = 0
		self.minValidationError = 2.5
		self.averageValidationError = 0

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
		for i in range(len(self.nNeurons)-1):
			self.biasWeights.append([random()-0.5 for j in range(self.nNeurons[i+1])])
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
				self.neurons[i+1][j] += self.biasWeights[(i+1)-1][j]
				self.neurons[i+1][j] = self.sig(self.neurons[i+1][j])
		#

		#--- Calculo do erro total ---#
		self.totalError = 0
		for i in range(5):
			self.totalError += (expected[i] - self.neurons[len(self.nNeurons)-1][i])**2
		self.totalError /= 2
		self.lastErrors[self.lastErrorsIndex] = self.totalError
		self.lastErrorsIndex = (self.lastErrorsIndex + 1) % self.lastErrorsSize
		#

		#--- Estatisticas ---#
		self.averageTrainingError += self.totalError
		if self.totalError < self.minTrainingError:
			self.minTrainingError = self.totalError
		#

		#--- Condicao de paragem ---#
		if 1.0*sum(self.lastErrors)/len(self.lastErrors) < self.stopCondition:
			return
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
			for k in range(self.nNeurons[i+1]):
				self.biasWeights[(i+1)-1][k] += self.learningFactor * deltas[i+1][k] * (self.neurons[i+1][k] * (1 - self.neurons[i+1][k]))
		#

	def validateNeuralNetwork(self, case):

		#--- Coloca o input na primeira camada de neuronios ---#
		self.neurons[0] = case[0]
		#

		#--- Criacao de array de valor esperado ---#
		expected = case[1]
		#

		#--- Calculo de valores de neuronios e output ---#
		for i in range(len(self.nNeurons)-1):
			for j in range(self.nNeurons[i+1]):
				self.neurons[i+1][j] = 0
				for k in range(self.nNeurons[i]):
					self.neurons[i+1][j] += self.neurons[i][k] * self.weights[i][k][j]
				self.neurons[i+1][j] += self.biasWeights[(i+1)-1][j]
				self.neurons[i+1][j] = self.sig(self.neurons[i+1][j])
		#

		#--- Calculo do erro total ---#
		self.totalError = 0
		for i in range(5):
			self.totalError += (expected[i] - self.neurons[len(self.nNeurons)-1][i])**2
		self.totalError /= 2
		#

		#--- Estatisticas ---#
		self.averageValidationError += self.totalError
		if self.totalError < self.minValidationError:
			self.minValidationError = self.totalError
		if expected[self.neurons[len(self.nNeurons)-1].index(max(self.neurons[len(self.nNeurons)-1]))] == 1:
			self.correctCases += 1
		#


	#--- Le a rede neuronal do ficheiro ---#
	def readNetwork(self, network):
		import cPickle, os
		file = open(network, 'r')
		content = cPickle.load(file)
		self.neurons = content[0]
		self.weights = content[1]
		self.biasWeights = content[2]
		file.close()
	#

	#--- Guarda rede neuronal em ficheiro ---#
	def writeNetwork(self, network):
		import cPickle, os
		file = open(network, 'w')
		cPickle.dump([self.neurons, self.weights, self.biasWeights], file) 
		file.close()
	#

	def loadNeuronalNetwork(self):
		import cPickle, os

		#network = "network/factor/network_0.02.iia"
		network = "network/factor/network_0.10.iia"
		#network = "network/factor/network_0.50.iia"

		#network = "network/tests/network_2.iia"
		#network = "network/tests/network_20.iia"
		#network = "network/tests/network_200.iia"
		#network = "network/tests/network_2000.iia"
		#network = "network/tests/network_4940.iia"

		network = "network/network.iia"

		#--- Se a rede ja estiver criada, apenas le os dados ---#
		if os.path.isfile(network):
			self.readNetwork(network)
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
			shuffle(fileNames)
			#

			#--- Criacao e inicializacao da rede neuronal ---#
			self.initialization()
			#

			#--- Treino da rede neuronal ---#
			self.numFiles = 0
			self.numCases = 0
			fileNamesTraining = fileNames[:int(len(fileNames)*self.percTrainingFiles)]
			
			files = loadFilesFromList(fileNamesTraining)
			shuffle(files)
			for file in files:
				self.numFiles += 1
				shuffle(file)
				for case in file:
					self.numCases += 1
					self.trainNeuralNetwork(case)
					#--- Condicao de paragem ---#
					if 1.0*sum(self.lastErrors)/len(self.lastErrors) < self.stopCondition:
						break
					#
				#--- Condicao de paragem ---#
				if 1.0*sum(self.lastErrors)/len(self.lastErrors) < self.stopCondition:
					break
				#

			print

			print "Number of Files Trained:", self.numFiles
			print "Number of Cases Trained:", self.numCases
			print "Minimum Training Total Error:", self.minTrainingError
			print "Average Training Total Error:", self.averageTrainingError/self.numCases

			self.writeNetwork(network)
			#

			print

			#--- Validacao da rede neuronal ---#
			self.numFiles = 0
			self.numCases = 0
			self.correctCases = 0
			fileNamesValidation = fileNames[int(len(fileNames)*self.percTrainingFiles):]

			files = loadFilesFromList(fileNamesValidation)
			shuffle(files)
			for file in files:
				self.numFiles += 1
				shuffle(file)
				for case in file:
					self.numCases += 1
					self.validateNeuralNetwork(case)

			print "Number of Files Validated:", self.numFiles
			print "Number of Cases Validated:", self.numCases
			print "Minimum Validation Total Error:", self.minValidationError
			print "Average Validation Total Error:", self.averageValidationError/self.numCases
			print "Number of Correct Cases:", self.correctCases
			print "Percentage of Correct Cases:", str(round(1.0*self.correctCases/self.numCases*100, 2)) + "%"

			print
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
				self.neurons[i+1][j] += self.biasWeights[(i+1)-1][j]
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

		return Directions.NUMBER[actions.index(max(actions))]
		#return self.getDirection(state, actions)

		
