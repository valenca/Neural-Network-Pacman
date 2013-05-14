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
import layout
from game import Agent
from random import choice
from util import getActionRepresentation, getStateRepresentation

class iiaPacmanAgent(Agent):

	def __init__(self, index = 0):
		self.scaredCounter = 0
		self.index = index
		self.keys = []
		self.trainingName = self.getTrainingName()
		print "Training name:", self.trainingName
		file = open(self.trainingName, 'w')
		file.close()

	def getTrainingName(self):
		import os.path
		name = "training_"
		count = 1
		while os.path.isfile("training/reactive/" + layout.lName + "/" + "default" + "/" + name + str(count) + ".iia"):
			count += 1
		return "training/reactive/" + layout.lName + "/" + "default" + "/" + name + str(count) + ".iia"
  
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
		#Prioridades:
			#Paredes
			#Fantasmas Normais (fugir)
			#Fantasmas Assustados (comer)
			#Capsulas
			#Pastilhas

		#--- Exclui Paredes ---#
		directions = state.getLegalActions()
		#

		#--- Exclui Paragem ---#
		directions.remove(Directions.STOP)
		#

		#--- Exclui Fantasmas Normais ---#
		for i in range(4):
			#Linhas
			if Directions.NUMBER[i] in directions:
				if stateRepresentation[8+i*2] == 1 or stateRepresentation[8+i*2+1] == 1:
					try:	 directions.remove(Directions.NUMBER[i])
					finally: False
			#Diagonais
			if Directions.NUMBER2[i] in directions:
				if stateRepresentation[8+8+i%4] == 1 or stateRepresentation[8+8+(i+1)%4] == 1:
					try:	 directions.remove(Directions.NUMBER2[i])
					finally: False

		if len(directions) == 0:	return choice(state.getLegalActions())
		elif len(directions) == 1:	return directions[0]
		#

		#--- Persegue Fantasmas Assustados ---#
		sgDirections = []

		for i in range(4):
			#Linhas 1 casa
			if Directions.NUMBER[i] in directions and Directions.NUMBER[i] not in sgDirections:
				if stateRepresentation[8+i*2] == -1:
					sgDirections.append(Directions.NUMBER[i])

		if len(sgDirections) > 0:	return choice(sgDirections)
		
		for i in range(4):
			#Linhas 2 casas
			if Directions.NUMBER[i] in directions and Directions.NUMBER[i] not in sgDirections:
				if stateRepresentation[8+i*2+1] == -1:
					sgDirections.append(Directions.NUMBER[i])
			#Diagonais
			if Directions.NUMBER2[i] in directions and Directions.NUMBER[i] not in sgDirections:
				if stateRepresentation[8+8+i%4] == -1 or stateRepresentation[8+8+(i+1)%4] == -1:
					sgDirections.append(Directions.NUMBER2[i])

		if len(sgDirections) > 0:	return choice(sgDirections)
		#

		#--- Persegue Capsulas ---#
		if self.scaredCounter:		self.scaredCounter -= 1
		else:
			cDirections = []

			for i in range(4):
				if Directions.NUMBER[i] in directions and Directions.NUMBER[i] not in cDirections:
					if stateRepresentation[i*2] == 1 and stateRepresentation[i*2+1] == 1:
						cDirections.append(Directions.NUMBER[i])

			if len(cDirections) > 0: return choice(cDirections)
		#

		#--- Persegue Pastilhas ---#
		gDirections = []

		for i in range(4):
			if Directions.NUMBER[i] in directions and Directions.NUMBER[i] not in gDirections:
				if stateRepresentation[i*2] == 1 and stateRepresentation[i*2+1] == 0:
					gDirections.append(Directions.NUMBER[i])

		if len(gDirections) > 0: return choice(gDirections)
		#

		try:	 directions.remove(Directions.REVERSE[state.getPacmanState().getDirection()])
		finally: return choice(directions)

class iiaGhostAgent(Agent):	 
  """Uses a strategy pattern to allow usage of different ghost behaviors in the game. 
  The strategy must receive an agent and a GameState as the arguments.
  To set the strategy through command line use:
  >>>pacman.py -g iiaGhostAgent --ghostArgs fnStrategy='fun1[;fun*]'
  example:
   python pacman.py -g iiaGhostAgent --ghostArgs fnStrategy='goweststrategy;defaultstrategy'
   or
   python pacman.py -g iiaGhostAgent --ghostArgs fnStrategy=goweststrategy;defaultstrategy
   depending on the version used

  You may add new arguments as long as you provide a proper constructor. """
  def __init__(self, index, fnStrategy='default'):
    self.index=index
    self.xCapsule = self.yCapsule = -1
    strategies = fnStrategy.split(';')
    try:
      self.strategy = util.lookup(strategies[index%len(strategies)], globals())
    except:
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
