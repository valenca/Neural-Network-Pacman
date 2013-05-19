"""
iiaAgents.py

Created by Rui Lopes on 2012-02-18.
Copyright (c) 2012 University of Coimbra. All rights reserved.
"""

"""
Alterado por
Alexandre Jesus - 2010130268
Gustavo Martins - 2010131414
Joao Valenca - 2010130607
"""

from pacman import Directions, SCARED_TIME, Actions
from game import Agent
from random import choice
import util
from util import getActionRepresentation, getStateRepresentation

class iiaPacmanAgent(Agent):

	def __init__(self, index = 0):
		self.scaredCounter = 0
		self.index = index
		self.keys = []
		self.trainingName = self.getTrainingName()

		global trainingN
		trainingN = self.trainingName

		print "Training name:", self.trainingName
		file = open(self.trainingName, 'w')
		file.close()

	def getTrainingName(self):
		import os.path
		name = "training_"
		count = 1
		while os.path.isfile("training/reactive/mediumClassic/all/" + name + str(count) + ".iia"):
			count += 1
		return "training/reactive/mediumClassic/all/" + name + str(count) + ".iia"
		
	def saveTraining(self, currentStuff):
		import cPickle
		try:
			file = open(self.trainingName, 'r')
			oldStuff = cPickle.load(file)
			file.close()
		except EOFError:
			oldStuff = []
		file = open(self.trainingName, 'w')
		#print "Now saving:", oldStuff + [currentStuff]
		#print "Adding:", currentStuff[0]
		cPickle.dump(oldStuff + [currentStuff], file) 
		file.close()

	def getAction( self, state):
		#from graphicsUtils import wait_for_keys
		legal = state.getLegalActions(self.index)
		stateRepresentation = getStateRepresentation(state)
		#print "State Representation:", stateRepresentation
		move = None
		while move == None:
			#self.keys = wait_for_keys()
			move = self.getMove(state, stateRepresentation)
			if move == None:
				print "Illegal move. Try again"
		
		actionRepresentation = getActionRepresentation(move)
		#print "Action Representation:", actionRepresentation
		self.saveTraining([stateRepresentation, actionRepresentation])
		return move

	def getMove(self, state, stateRepresentation):

		"""for i in range(10,-1,-1):
			for j in range(20):
				print stateRepresentation[(i*40) + j*2 : (i*40) + j*2 + 2],
			print

		for i in range(10,-1,-1):
			for j in range(20):
				print stateRepresentation[440 + (i*80) + (j*4) : 440 + (i*80) + (j*4) + 2],
				print stateRepresentation[440 + (i*80) + (j*4) + 2 : 440 + (i*80) + (j*4) + 4],
			print
		exit()"""

		#Decrementa o contador de efeito da capsula
		if self.scaredCounter:
			self.scaredCounter -= 1

		#Se um fantasma tem o seu contador de assustado a SCARED_TIME entao o pacman acabou de comer uma capsula
		if state.getNumAgents() > 1 and state.getGhostState(1).scaredTimer == SCARED_TIME-1:
			self.scaredCounter = SCARED_TIME-1;


		directions = state.getLegalPacmanActions()
		directions.remove(Directions.STOP)

		#Se houver fantasmas normais nas esquinas, muda para a direcao oposta;
		directions = hasGhostsOnCorner(state, directions)

		#Elimina caminhos com fantasmas normais a, no maximo, 2 casas;
		withoutGhosts = hasNormalGhosts(state, 2, directions)
		if len(withoutGhosts) == 1:
			return withoutGhosts[0]
		elif len(withoutGhosts) == 0:
			if(state.getPacmanState().getDirection() in state.getLegalPacmanActions()):
				return state.getPacmanState().getDirection()
			else:
				return choice(directions)

		directions = withoutGhosts;


		#Se houver fantasma assustado, dirige-se a ele
		withScaredGhosts = hasScaredGhosts(state, directions)
		if len(withScaredGhosts) >= 1:
			return choice(withScaredGhosts)


		#Se nao estiver com o efeito de uma capsula
		if not self.scaredCounter:
			#Se houver capsula na linha de vista, dirige-se a ela;
			withCapsules = hasNearCapsule(state, directions)
			if len(withCapsules) >= 1:
				return choice(withCapsules)


		#Se continuar a existir mais que um caminho, escolhe o que tem a pastilha segura mais proxima;
		withNearFood = hasNearFood(state, directions)
		if len(withNearFood) == 1:
			return withNearFood[0]
		elif len(withNearFood) > 1:
			return choice(withNearFood)

		#Se so restar um caminho
		if len(directions) == 1:
			return directions[0]
		#Se ainda continuar a existir mais que um caminho, escolhe aleatoriamente.
		try:
			directions.remove(Directions.REVERSE[state.getPacmanState().getDirection()])
		finally:
			return choice(directions)

#Verifica se existe algum fantasma nas quatro diagonais de um quadrado de distancia
#Se houver tira as duas direcoes coorrespondentes da lista legalPaths
def hasGhostsOnCorner(state, directions):
	legalPaths = directions[:]

	xPac = state.getPacmanState().getPosition()[0]
	yPac = state.getPacmanState().getPosition()[1]

	#Acima esquerda
	if (not state.hasWall(xPac - 1, yPac + 1)):
		if hasGhost(state, xPac - 1, yPac + 0.5, 0) or hasGhost(state, xPac - 1, yPac + 1, 0) or hasGhost(state, xPac - 1, yPac + 1.5, 0):
			if Directions.NORTH in legalPaths:
				legalPaths.remove(Directions.NORTH)
			if Directions.LEFT in legalPaths:
				legalPaths.remove(Directions.LEFT)

	#Acima direita
	if (not state.hasWall(xPac + 1, yPac + 1)):
		if hasGhost(state, xPac + 1, yPac + 0.5, 0) or hasGhost(state, xPac + 1, yPac + 1, 0) or hasGhost(state, xPac + 1, yPac + 1.5, 0):
			if Directions.NORTH in legalPaths:
				legalPaths.remove(Directions.NORTH)
			if Directions.RIGHT in legalPaths:
				legalPaths.remove(Directions.RIGHT)

	#Abaixo esquerda
	if (not state.hasWall(xPac - 1, yPac - 1)):
		if hasGhost(state, xPac - 1, yPac - 0.5, 0) or hasGhost(state, xPac - 1, yPac - 1, 0) or hasGhost(state, xPac - 1, yPac - 1.5, 0):
			if Directions.SOUTH in legalPaths:
				legalPaths.remove(Directions.SOUTH)
			if Directions.LEFT in legalPaths:
				legalPaths.remove(Directions.LEFT)

	#Abaixo direita
	if (not state.hasWall(xPac + 1, yPac - 1)):
		if hasGhost(state, xPac + 1, yPac - 0.5, 0) or hasGhost(state, xPac + 1, yPac - 1, 0) or hasGhost(state, xPac + 1, yPac - 1.5, 0):
			if Directions.SOUTH in legalPaths:
				legalPaths.remove(Directions.SOUTH)
			if Directions.RIGHT in legalPaths:
				legalPaths.remove(Directions.RIGHT)

	return legalPaths

#Verifica se um fantasma esta num beco
def isGhostInAlley(state, ghost):
	ghostP = ghost.getPosition()
	if state.hasWall(int(ghostP[0]+0.5) + Actions._directions[Directions.LEFT[ghost.getDirection()]][0], int(ghostP[1]+0.5) + Actions._directions[Directions.LEFT[ghost.getDirection()]][1]):
		if state.hasWall(int(ghostP[0]+0.5) + Actions._directions[ghost.getDirection()][0], int(ghostP[1]+0.5) + Actions._directions[ghost.getDirection()][1]):
			if state.hasWall(int(ghostP[0]+0.5) + Actions._directions[Directions.RIGHT[ghost.getDirection()]][0], int(ghostP[1]+0.5) + Actions._directions[Directions.RIGHT[ghost.getDirection()]][1]):
				return True
	return False

#Verifica se existe fantasmas normais a, no maximo 'ran' casas de distancia, para cada direcao
def hasNormalGhosts(state, ran, directions):
	legalPaths = directions[:]

	xPac = state.getPacmanState().getPosition()[0]
	yPac = state.getPacmanState().getPosition()[1]
	
	if Directions.NORTH in legalPaths:
		ghost = isNSGhostInDirection(state, Actions._directions[Directions.NORTH], 0)
		if ghost and (0 < (ghost[2] - yPac) <= ran):
			if state.getGhostState(ghost[0]).getDirection() != Directions.NORTH:
				legalPaths.remove(Directions.NORTH)
			elif isGhostInAlley(state, state.getGhostState(ghost[0])):
				legalPaths.remove(Directions.NORTH)

	if Directions.SOUTH in legalPaths:
		ghost = isNSGhostInDirection(state, Actions._directions[Directions.SOUTH], 0)
		if ghost and (-ran <= (ghost[2] - yPac) < 0):
			if state.getGhostState(ghost[0]).getDirection() != Directions.SOUTH:
				legalPaths.remove(Directions.SOUTH)
			elif isGhostInAlley(state, state.getGhostState(ghost[0])):
				legalPaths.remove(Directions.SOUTH)

	if Directions.EAST in legalPaths:
		ghost = isNSGhostInDirection(state, Actions._directions[Directions.EAST], 0)
		if ghost and (0 < (ghost[1] - xPac) <= ran):
			if state.getGhostState(ghost[0]).getDirection() != Directions.EAST:
				legalPaths.remove(Directions.EAST)
			elif isGhostInAlley(state, state.getGhostState(ghost[0])):
				legalPaths.remove(Directions.EAST)

	if Directions.WEST in legalPaths:
		ghost = isNSGhostInDirection(state, Actions._directions[Directions.WEST], 0)
		if ghost and (-ran <= (ghost[1] - xPac) < 0):
			if state.getGhostState(ghost[0]).getDirection() != Directions.WEST:
				legalPaths.remove(Directions.WEST)
			elif isGhostInAlley(state, state.getGhostState(ghost[0])):
				legalPaths.remove(Directions.WEST)

	return legalPaths

#Devolve o indice e a posicao do primeiro fantasma encontrado numa direcao
#Se nao encontrar devolve False
def isNSGhostInDirection(state, inc, scared):
	x = state.getPacmanState().getPosition()[0] + inc[0]/2.0
	y = state.getPacmanState().getPosition()[1] + inc[1]/2.0

	#Enquanto nao chegar a parede
	while not state.hasWall(int(x), int(y)):
		ghost = hasGhost(state, x, y, scared)
		if ghost:
			return (ghost, x, y)
		x += inc[0]/2.0
		y += inc[1]/2.0

	return False

#Dos caminhos disponiveis remove aqueles que nao tem fantasmas assustados e devolve os que tem
def hasScaredGhosts(state, directions):
	withScaredGhosts = directions[:]
	for i in range(len(directions)):
		if not isNSGhostInDirection(state, Actions._directions[directions[i]], 1):
			withScaredGhosts.remove(directions[i])
	return withScaredGhosts

#Devolve o caminho, ou caminhos, com a capsula mais perto
def hasNearCapsule(state, directions):
	withNearCapsule = []
	nearCapsule = -1
	for i in range(len(directions)):
		capsule = nearCapsuleInDirectionPacman(state, Actions._directions[directions[i]])
		if capsule == nearCapsule:
			withNearCapsule.append(directions[i])
		elif capsule > 0 and (capsule < nearCapsule or nearCapsule == -1):
			withNearCapsule = [directions[i]]
			nearCapsule = capsule
	return withNearCapsule

#Devolve a distancia a uma capsula numa determinada direcao, devolve 0 se nao houver
def nearCapsuleInDirectionPacman(state, inc):
	ghost = isNSGhostInDirection(state, inc, 0)

	x = state.getPacmanState().getPosition()[0] + inc[0]
	y = state.getPacmanState().getPosition()[1] + inc[1]
	capsule = 1

	#Se o limite de procura for uma parede
	if not ghost:
		while not state.hasWall(x, y):
			if (x, y) in state.getCapsules():
				return capsule
			x += inc[0]
			y += inc[1]
			capsule += 1
	#Se o limite de procura for o meio caminho entre o pacman e um fantasma
	else:
		xPac = state.getPacmanState().getPosition()[0]
		yPac = state.getPacmanState().getPosition()[1]
		#Norte e Este
		if inc[0] == 1 or inc[1] == 1:
			while x <= ((ghost[0]-xPac-1)/2)+xPac and y <= ((ghost[1]-yPac-1)/2)+yPac:
				if (x, y) in state.getCapsules():
					return capsule
				x += inc[0]
				y += inc[1]
				capsule += 1
		#Sul e Oeste
		else:
			while x >= ((ghost[0]-xPac+1)/2)+xPac and y >= ((ghost[1]-yPac+1)/2)+yPac:
				if (x, y) in state.getCapsules():
					return capsule
				x += inc[0]
				y += inc[1]
				capsule += 1

	return 0

#Devolve o caminho, ou caminhos, com a pastilha mais perto
def hasNearFood(state, directions):
	withNearFood = []
	nearFood = -1
	for i in range(len(directions)):
		food = nearFoodInDirection(state, Actions._directions[directions[i]])
		if food == nearFood:
			withNearFood.append(directions[i])
		elif food > 0 and (food < nearFood or nearFood == -1):
			withNearFood = [directions[i]]
			nearFood = food
	return withNearFood

#Devolve a distancia a uma pastilha numa determinada direcao, devolve 0 se nao houver
def nearFoodInDirection(state, inc):
	ghost = isNSGhostInDirection(state, inc, 0)

	x = state.getPacmanState().getPosition()[0] + inc[0]
	y = state.getPacmanState().getPosition()[1] + inc[1]
	food = 1

	#Se o limite de procura for uma parede
	if not ghost:
		while not state.hasWall(x, y):
			if state.hasFood(x, y):
				return food
			x += inc[0]
			y += inc[1]
			food += 1
	#Se o limite de procura for o meio caminho entre o pacman e um fantasma
	else:
		xPac = state.getPacmanState().getPosition()[0]
		yPac = state.getPacmanState().getPosition()[1]
		#Norte e Este
		if inc[0] == 1 or inc[1] == 1:
			while x <= ((ghost[0]-xPac-1)/2)+xPac and y <= ((ghost[1]-yPac-1)/2)+yPac:
				if state.hasFood(x, y):
					return food
				x += inc[0]
				y += inc[1]
				food += 1
		#Sul e Oeste
		else:
			while x >= ((ghost[0]-xPac+1)/2)+xPac and y >= ((ghost[1]-yPac+1)/2)+yPac:
				if state.hasFood(x, y):
					return food
				x += inc[0]
				y += inc[1]
				food += 1

	return 0

class iiaGhostAgent(Agent):	 
	"""Uses a strategy pattern to allow usage of different ghost behaviors in the game. 
	The strategy must receive an agent and a GameState as the arguments.
	To set the strategy through command line use:
	>>>pacman.py -g iiaGhostAgent --ghostArgs fnStrategy='fun1[;fun*]'
	You may add new arguments as long as you provide a proper constructor. """
	def __init__(self, index, fnStrategy='defaultstrategy'):
		self.index=index
		self.xCapsule = self.yCapsule = -1
		strategies = fnStrategy.split(';')

		try:
			self.strategy = util.lookup(strategies[index%len(strategies)], globals())
		except:
			print "Function "+strategies[index%len(strategies)]+" not defined!"
			self.strategy = default
 
	def getAction(self, state):
		"""The agent receives a GameState (defined in pacman.py).
		 Simple random ghost agent."""
		return self.strategy( self, state )
	
def default(agent,state):
	return choice(state.getLegalActions(agent.index))

def gowest(agent,state):
	if Directions.WEST in state.getLegalActions(agent.index):
		return Directions.WEST
	else:
		return choice(state.getLegalActions(agent.index))

def gonorth(agent,state):
	if Directions.NORTH in state.getLegalActions(agent.index):
		return Directions.NORTH
	else:
		return choice(state.getLegalActions(agent.index))

def goeast(agent,state):
	if Directions.EAST in state.getLegalActions(agent.index):
		return Directions.EAST
	else:
		return choice(state.getLegalActions(agent.index))

def gosouth(agent,state):
	if Directions.SOUTH in state.getLegalActions(agent.index):
		return Directions.SOUTH
	else:
		return choice(state.getLegalActions(agent.index))

#Fantasma Chaser
def chaser(agent,state,fearful=False,directions=False):

	if not fearful:
		directions = state.getLegalActions(agent.index)

	#Se vir o pacman nas diagonais, segue-o
	withPacman = hasPacmanOnCorners(agent, state, directions)
	if len(withPacman) >= 1:
		return choice(withPacman)

	#Se vir o pacman numa direcao, segue-o
	withPacman = hasPacmanGhost(agent, state, directions)
	if len(withPacman) == 1:
		return withPacman[0]

	return choice(directions)

#Fantasma Fearful/Ambusher
def fearful(agent,state):

	directions = state.getLegalActions(agent.index)

	#Se vir um fantasma tenta n ir atras dele
	withoutGhosts = hasGhosts(agent, state, directions)
	if len(withoutGhosts) == 1:
		return withoutGhosts[0]
	if len(withoutGhosts) > 1:
		directions = withoutGhosts

	#Se tiver assustado tenta fugir do pacman
	if state.getGhostState(agent.index).scaredTimer:
		withoutPacman = directions[:]
		withPacmanCorners = hasPacmanOnCorners(agent, state, directions)
		withPacman = hasPacmanGhost(agent, state, directions)
		for i in withPacmanCorners:
			if i in withoutPacman:
				withoutPacman.remove(i)
		for i in withPacman:
			if i in withoutPacman:
				withoutPacman.remove(i)

		if len(withoutPacman) >= 1:
			return choice(withoutPacman)
		return choice(directions)

	#Se nao tiver assustado comporta-se como o Chaser
	return chaser(agent, state, 1, directions)

#Fantasma Guardian
def guardian(agent,state):
	directions = state.getLegalActions(agent.index)

	#Caso nao tenha capsula marcada vai procurar uma
	if agent.xCapsule == -1:
		capsulePos = isCapsule(agent, state, directions)
		if capsulePos:
			agent.xCapsule = capsulePos[0]
			agent.yCapsule = capsulePos[1]

	#Caso tenha uma capsula marcada ou acabado de encontrar uma vai verificar se ainda la esta (se a vir)
	if agent.xCapsule != -1:
		#Se consegue ver a posicao marcada
		if seePosition(agent, state):
			#Se a capsula ja la nao estiver
			if not (agent.xCapsule, agent.yCapsule) in state.getCapsules():
				agent.xCapsule = agent.yCapsule = -1

	#Se vir que a capsula ainda esta la, ou se nao vir a marcacao da capsula, tenta ir para esta
	if agent.xCapsule != -1:
		return chooseDirection(agent, state, directions)

	#Se nao tiver capsula marcada e nao tiver encontrado nenhuma, comporta-se como o Chaser
	return chaser(agent, state, 1, directions)

def hasPacmanOnCorners(agent, state, directions):
	withPacman = []
	x = state.getGhostPosition(agent.index)[0]
	y = state.getGhostPosition(agent.index)[1]

	#Acima esquerda
	if (not state.hasWall(int(x) - 1, int(y) + 1)) and hasPacman(state, int(x) - 1, int(y) + 1):
		if Directions.NORTH in directions:
			withPacman.append(Directions.NORTH)
		if Directions.LEFT in directions:
			withPacman.append(Directions.LEFT)

	#Acima direita
	elif (not state.hasWall(int(x) + 1, int(y) + 1)) and hasPacman(state, int(x) + 1, int(y) + 1):
		if Directions.NORTH in directions:
			withPacman.append(Directions.NORTH)
		if Directions.RIGHT in directions:
			withPacman.append(Directions.RIGHT)

	#Abaixo esquerda
	elif (not state.hasWall(int(x) - 1, int(y) - 1)) and hasPacman(state, int(x) - 1, int(y) - 1):
		if Directions.SOUTH in directions:
			withPacman.append(Directions.SOUTH)
		if Directions.LEFT in directions:
			withPacman.append(Directions.LEFT)

	#Abaixo direita
	elif (not state.hasWall(int(x) + 1, int(y) - 1)) and hasPacman(state, int(x) + 1, int(y) - 1):
		if Directions.SOUTH in directions:
			withPacman.append(Directions.SOUTH)
		if Directions.RIGHT in directions:
			withPacman.append(Directions.RIGHT)

	return withPacman

#Verifica se o Pacman esta na linha de vista
def hasPacmanGhost(agent,state,directions):
	withPacman = directions[:]
	for i in range(len(directions)):
		if not isPacmanInDirection(agent, state, Actions._directions[directions[i]]):
			withPacman.remove(directions[i])
	return withPacman

#Verifica se o Pacman esta numa direcao
def isPacmanInDirection(agent,state,inc):
	x = state.getGhostPosition(agent.index)[0] + inc[0]/2.0
	y = state.getGhostPosition(agent.index)[1] + inc[1]/2.0

	#Enquanto nao chegar a parede
	while not state.hasWall(int(x), int(y)):
		if hasPacman(state, x, y):
			return True
		x += inc[0]/2.0
		y += inc[1]/2.0

	return False

#Devolve os caminhos sem fantasmas
def hasGhosts(agent, state, directions):
	withoutGhosts = directions[:]
	for i in range(len(directions)):
		if isGhostInDirection(agent, state, Actions._directions[directions[i]]):
			withoutGhosts.remove(directions[i])
	return withoutGhosts

#Verifica se existe um fantasma numa direcao
def isGhostInDirection(agent, state, inc):
	x = state.getGhostPosition(agent.index)[0] + inc[0]/2.0
	y = state.getGhostPosition(agent.index)[1] + inc[1]/2.0

	#Enquanto nao chegar a parede
	while not state.hasWall(int(x), int(y)):
		if hasGhost(state, x, y, 0) or hasGhost(state, x, y, 1):
			return True
		x += inc[0]/2.0
		y += inc[1]/2.0

	return False

#Devolve a posicao da capsula mais proxima
def isCapsule(agent, state, directions):
	xNearCapsule = yNearCapsule = -1
	nearCapsule = -1
	for i in range(len(directions)):
		capsule = nearCapsuleInDirectionGhost(agent, state, Actions._directions[directions[i]])
		if capsule[0] > 0 and (capsule[0] < nearCapsule or nearCapsule == -1):
			xNearCapsule = capsule[1]
			yNearCapsule = capsule[2]
			nearCapsule = capsule[0]
	return (xNearCapsule, yNearCapsule)

#Devolve a distancia a uma capsula numa determinada direcao, devolve 0 se nao houver
def nearCapsuleInDirectionGhost(agent, state, inc):
	x = state.getGhostPosition(agent.index)[0] + inc[0]/2.0
	y = state.getGhostPosition(agent.index)[1] + inc[1]/2.0
	capsule = 1

	while not state.hasWall(int(x), int(y)):
		if (x, y) in state.getCapsules():
			return (capsule, x, y)
		x += inc[0]/2.0
		y += inc[1]/2.0
		capsule += 1

	return (0, -1, -1)

#Verifica se consegue ver determinada posicao do mapa
def seePosition(agent, state):
	xSelf = state.getGhostPosition(agent.index)[0]
	ySelf = state.getGhostPosition(agent.index)[1]
	inc = [-1, -1]

	if xSelf == agent.xCapsule:
		inc[0] = 0
		if ySelf == agent.yCapsule:
			return True
		elif ySelf < agent.yCapsule:
			inc[1] = 1
		else:
			inc[1] = -1
	elif ySelf == agent.yCapsule:
		inc[1] = 0
		if xSelf < agent.xCapsule:
			inc[0] = 1
		else:
			inc[0] = -1

	if inc[0] != -1:
		x = state.getGhostPosition(agent.index)[0]
		y = state.getGhostPosition(agent.index)[1]
		while not state.hasWall(int(x), int(y)):
			if x == agent.xCapsule and y == agent.yCapsule:
				return True
			x += inc[0]/2.0
			y += inc[1]/2.0

	return False

#Escolhe a direcao a tomar tendo em conta que tem uma capsula marcada
def chooseDirection(agent, state, directions):
	xSelf = state.getGhostPosition(agent.index)[0]
	ySelf = state.getGhostPosition(agent.index)[1]

	if xSelf < agent.xCapsule:
		if ySelf < agent.yCapsule:
			if Directions.NORTH in directions:
				return Directions.NORTH
			if Directions.EAST in directions:
				return Directions.EAST
		elif ySelf == agent.yCapsule:
			return goeast(agent, state)
		else:
			if Directions.SOUTH in directions:
				return Directions.SOUTH
			if Directions.EAST in directions:
				return Directions.EAST
	elif xSelf == agent.xCapsule:
		if ySelf < agent.yCapsule:
			return gonorth(agent, state)
		elif ySelf > agent.yCapsule:
			return gosouth(agent, state)
	else:
		if ySelf < agent.yCapsule:
			if Directions.NORTH in directions:
				return Directions.NORTH
			if Directions.WEST in directions:
				return Directions.WEST
		elif ySelf == agent.yCapsule:
			return gowest(agent, state)
		else:
			if Directions.SOUTH in directions:
				return Directions.SOUTH
			if Directions.WEST in directions:
				return Directions.WEST

	return choice(directions)

#Verifica se existe um Fantasma (assustado ou nao) numa determinada posicao
def hasGhost(state, x, y, scared):
	ghosts = state.getGhostPositions()
	for i in xrange(len(ghosts)):
		if not scared:
			if state.getGhostState(i+1).scaredTimer == 0 and x == ghosts[i][0] and y == ghosts[i][1]:
				return i+1
		else:
			if state.getGhostState(i+1).scaredTimer > 0 and x == ghosts[i][0] and y == ghosts[i][1]:
				return i+1
	return False

#Verifica se existe o Pacman numa determinada posicao
def hasPacman(state, x, y):
	if x == state.getPacmanPosition()[0] and y == state.getPacmanPosition()[1]:
		return True
	return False
