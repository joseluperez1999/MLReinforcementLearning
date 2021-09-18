# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

    "Funcion que proporciona los datos para la practica 1"
    def printLineData(self, gameState, PMs, distGhosts, wasParedN, wasParedS, wasParedW, wasParedE, scores):

        #Posicion del Pacman hace 2 turnos
        PMs[2] = PMs[1]
        PMs[1] = PMs[0]
        PMs[0] = gameState.getPacmanPosition()
        pacmanPosition = PMs[2]
        strPacmanPosition = ""
        for i in pacmanPosition:
            strPacmanPosition = strPacmanPosition + str(i) + " , "

        #Distancias a los fantasmas hace 2 turnos
        distGhosts[2] = distGhosts[1]
        distGhosts[1] = distGhosts[0]
        distGhosts[0] = gameState.data.ghostDistances
        distManG = distGhosts[2]
        strGhostDistances = ""
        for i in distManG:
            if i == None:
                i = -1
            strGhostDistances = strGhostDistances + str(i) + " , "

        #Es pared los ultimos 3 turnos
        legalActions = gameState.getLegalActions()
            #wasParedN
        wasParedN[2] = wasParedN[1]
        wasParedN[1] = wasParedN[0]
        if "North" in legalActions:
            wasParedN[0] = 0
        else:
            wasParedN[0] = 1

            #wasParedS
        wasParedS[2] = wasParedS[1]
        wasParedS[1] = wasParedS[0]
        if "South" in legalActions:
            wasParedS[0] = 0
        else:
            wasParedS[0] = 1

            #wasParedW
        wasParedW[2] = wasParedW[1]
        wasParedW[1] = wasParedW[0]
        if "West" in legalActions:
            wasParedW[0] = 0
        else:
            wasParedW[0] = 1

            #wasParedE
        wasParedE[2] = wasParedE[1]
        wasParedE[1] = wasParedE[0]
        if "East" in legalActions:
            wasParedE[0] = 0
        else:
            wasParedE[0] = 1

        strIsPared = str(wasParedN[0]) + " , " + str(wasParedS[0]) + " , " + str(wasParedW[0]) + " , " + str(wasParedE[0]) + " , "

        #Puntuaciones los ultimos 3 turnos
        scores[0] = scores[1]
        scores[1] = scores[2]
        scores[2] = gameState.getScore()

        score0 = scores[0]
        score1 = scores[1]
        score2 = scores[2]

        strScores = str(score0) + " , " + str(score1) + " , " + str(score2)
        data = strPacmanPosition + strGhostDistances + strIsPared + strScores + '\n'

        #Los dos primeros turnos no se imprimen ya que tenemos que esperar ha tener informacion de 3 turnos
        if self.countActions <= 2:
            return ""

        return data


class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)
        self.countActions = 0

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        return KeyboardAgent.getAction(self, gameState)

    "Funcion que proporciona los datos para la practica 1"
    def printLineData(self, gameState, PMs, distGhosts, posGhosts, wasParedN, wasParedS, wasParedW, wasParedE, scores, actionsChoosed):

        #Posicion del Pacman hace 3 turnos
        PMs[3] = PMs[2]
        PMs[2] = PMs[1]
        PMs[1] = PMs[0]
        PMs[0] = gameState.getPacmanPosition()
        pacmanPosition = PMs[3]
        strPacmanPosition = ""
        for i in pacmanPosition:
            strPacmanPosition = strPacmanPosition + str(i) + " , "

        #Distancias a los fantasmas hace 3 turnos
        distGhosts[3] = distGhosts[2]
        distGhosts[2] = distGhosts[1]
        distGhosts[1] = distGhosts[0]
        distGhosts[0] = gameState.data.ghostDistances
        distManG = distGhosts[3]
        strGhostDistances = ""
        #Se calcula el fantasma mas cercano
        nearest = 100000
        for i in distManG:
            if i < nearest and i is not None:
                nearest = i
        strGhostDistances = str(nearest) + " , "

        #Posiciones de los fantasmas hace 3 turnos
        posGhosts[3] = posGhosts[2]
        posGhosts[2] = posGhosts[1]
        posGhosts[1] = posGhosts[0]
        posGhosts[0] = gameState.getGhostPositions()

        #Posicion relativa al fantasma mas cercano
        nearestGhostIndex = distManG.index(nearest)
        nearestGhostPos = posGhosts[3][nearestGhostIndex]
        relX = pacmanPosition[0] - nearestGhostPos[0]
        relY = pacmanPosition[1] - nearestGhostPos[1]
        strRelX = str(relX) + " , "
        strRelY = str(relY) + " , "


        #Es pared los ultimos 3 turnos
        legalActions = gameState.getLegalActions()
            #wasParedN
        wasParedN[3] = wasParedN[2]
        wasParedN[2] = wasParedN[1]
        wasParedN[1] = wasParedN[0]
        if "North" in legalActions:
            wasParedN[0] = 0
        else:
            wasParedN[0] = 1

            #wasParedS
        wasParedS[3] = wasParedS[2]
        wasParedS[2] = wasParedS[1]
        wasParedS[1] = wasParedS[0]
        if "South" in legalActions:
            wasParedS[0] = 0
        else:
            wasParedS[0] = 1

            #wasParedW
        wasParedW[3] = wasParedW[2]
        wasParedW[2] = wasParedW[1]
        wasParedW[1] = wasParedW[0]
        if "West" in legalActions:
            wasParedW[0] = 0
        else:
            wasParedW[0] = 1

            #wasParedE
        wasParedE[3] = wasParedE[2]
        wasParedE[2] = wasParedE[1]
        wasParedE[1] = wasParedE[0]
        if "East" in legalActions:
            wasParedE[0] = 0
        else:
            wasParedE[0] = 1

        strIsPared = str(wasParedN[3]) + " , " + str(wasParedS[3]) + " , " + str(wasParedW[3]) + " , " + str(wasParedE[3]) + " , "

        #Puntuaciones los ultimos 3 turnos
        scores[0] = scores[1]
        scores[1] = scores[2]
        scores[2] = scores[3]
        scores[3] = gameState.getScore()

        score0 = scores[0]
        score1 = scores[1]
        score2 = scores[2]
        score3 = scores[3]

        strScores = str(score0) + " , " + str(score1) + " , " + str(score2) + " , " + str(score3)

        #Accion tomada por el pacman en el tick anterior
        oldAction = actionsChoosed[3]
        if oldAction is None:
            oldAction = Directions.STOP
        strOldAction = str(oldAction) + " , "

        #Direcciones tomadas por el pacman en los ultimos 3 turnos
        actionsChoosed[3] = actionsChoosed[2]
        actionsChoosed[2] = actionsChoosed[1]
        actionsChoosed[1] = actionsChoosed[0]
        actionsChoosed[0] = gameState.data.agentStates[0].getDirection()

        strDirection = " , " + str(actionsChoosed[3])
        #String data que se va a escribir en fichero
        data = strPacmanPosition + strRelX + strRelY + strGhostDistances + strIsPared + strOldAction + strScores + strDirection + '\n'

        #Los tres primeros turnos no se imprimen ya que tenemos que esperar a tener informacion de 4 turnos
        if self.countActions <= 3:
            return ""

        return data


from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    ''' Print the layout'''
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

    "Funcion que proporciona los datos para la practica 1"
    def printLineData(self, gameState, PMs, distGhosts, wasParedN, wasParedS, wasParedW, wasParedE, scores):

        #Posicion del Pacman hace 2 turnos
        PMs[2] = PMs[1]
        PMs[1] = PMs[0]
        PMs[0] = gameState.getPacmanPosition()
        pacmanPosition = PMs[2]
        strPacmanPosition = ""
        for i in pacmanPosition:
            strPacmanPosition = strPacmanPosition + str(i) + " , "

        #Distancias a los fantasmas hace 2 turnos
        distGhosts[2] = distGhosts[1]
        distGhosts[1] = distGhosts[0]
        distGhosts[0] = gameState.data.ghostDistances
        distManG = distGhosts[2]
        strGhostDistances = ""
        for i in distManG:
            if i == None:
                i = -1
            strGhostDistances = strGhostDistances + str(i) + " , "

        #Es pared los ultimos 3 turnos
        legalActions = gameState.getLegalActions()
            #wasParedN
        wasParedN[2] = wasParedN[1]
        wasParedN[1] = wasParedN[0]
        if "North" in legalActions:
            wasParedN[0] = 0
        else:
            wasParedN[0] = 1

            #wasParedS
        wasParedS[2] = wasParedS[1]
        wasParedS[1] = wasParedS[0]
        if "South" in legalActions:
            wasParedS[0] = 0
        else:
            wasParedS[0] = 1

            #wasParedW
        wasParedW[2] = wasParedW[1]
        wasParedW[1] = wasParedW[0]
        if "West" in legalActions:
            wasParedW[0] = 0
        else:
            wasParedW[0] = 1

            #wasParedE
        wasParedE[2] = wasParedE[1]
        wasParedE[1] = wasParedE[0]
        if "East" in legalActions:
            wasParedE[0] = 0
        else:
            wasParedE[0] = 1

        strIsPared = str(wasParedN[0]) + " , " + str(wasParedS[0]) + " , " + str(wasParedW[0]) + " , " + str(wasParedE[0]) + " , "

        #Puntuaciones los ultimos 3 turnos
        scores[0] = scores[1]
        scores[1] = scores[2]
        scores[2] = gameState.getScore()

        score0 = scores[0]
        score1 = scores[1]
        score2 = scores[2]

        strScores = str(score0) + " , " + str(score1) + " , " + str(score2)
        data = strPacmanPosition + strGhostDistances + strIsPared + strScores + '\n'

        #Los dos primeros turnos no se imprimen ya que tenemos que esperar ha tener informacion de 3 turnos
        if self.countActions <= 2:
            return ""

        return data


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

    "Funcion que proporciona los datos para la practica 1"
    def printLineData(self, gameState, PMs, distGhosts, wasParedN, wasParedS, wasParedW, wasParedE, scores):

        #Posicion del Pacman hace 2 turnos
        PMs[2] = PMs[1]
        PMs[1] = PMs[0]
        PMs[0] = gameState.getPacmanPosition()
        pacmanPosition = PMs[2]
        strPacmanPosition = ""
        for i in pacmanPosition:
            strPacmanPosition = strPacmanPosition + str(i) + " , "

        #Distancias a los fantasmas hace 2 turnos
        distGhosts[2] = distGhosts[1]
        distGhosts[1] = distGhosts[0]
        distGhosts[0] = gameState.data.ghostDistances
        distManG = distGhosts[2]
        strGhostDistances = ""
        for i in distManG:
            if i == None:
                i = -1
            strGhostDistances = strGhostDistances + str(i) + " , "

        #Es pared los ultimos 3 turnos
        legalActions = gameState.getLegalActions()
            #wasParedN
        wasParedN[2] = wasParedN[1]
        wasParedN[1] = wasParedN[0]
        if "North" in legalActions:
            wasParedN[0] = 0
        else:
            wasParedN[0] = 1

            #wasParedS
        wasParedS[2] = wasParedS[1]
        wasParedS[1] = wasParedS[0]
        if "South" in legalActions:
            wasParedS[0] = 0
        else:
            wasParedS[0] = 1

            #wasParedW
        wasParedW[2] = wasParedW[1]
        wasParedW[1] = wasParedW[0]
        if "West" in legalActions:
            wasParedW[0] = 0
        else:
            wasParedW[0] = 1

            #wasParedE
        wasParedE[2] = wasParedE[1]
        wasParedE[1] = wasParedE[0]
        if "East" in legalActions:
            wasParedE[0] = 0
        else:
            wasParedE[0] = 1

        strIsPared = str(wasParedN[0]) + " , " + str(wasParedS[0]) + " , " + str(wasParedW[0]) + " , " + str(wasParedE[0]) + " , "

        #Puntuaciones los ultimos 3 turnos
        scores[0] = scores[1]
        scores[1] = scores[2]
        scores[2] = gameState.getScore()

        score0 = scores[0]
        score1 = scores[1]
        score2 = scores[2]

        strScores = str(score0) + " , " + str(score1) + " , " + str(score2)
        data = strPacmanPosition + strGhostDistances + strIsPared + strScores + '\n'

        #Los dos primeros turnos no se imprimen ya que tenemos que esperar ha tener informacion de 3 turnos
        if self.countActions <= 2:
            return ""

        return data

class BasicAgentAA(BustersAgent):

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        BustersAgent.__init__(self, index, inference, ghostAgents)
        self.epsilon = 0.3
        self.alpha = 0.4
        self.discount = 0.75
        self.table_file = open("qtable.txt", "r+")
        self.q_table = self.readQtable()
        self.actions=[Directions.NORTH,Directions.SOUTH,Directions.WEST,Directions.EAST]
        self.columAction={Directions.NORTH:0,Directions.SOUTH:1,Directions.WEST:2,Directions.EAST:3} #Este diccionario identifica la accion con su columna en la qtable
        self.reward=0
        self.lastState=None
        self.move = Directions.STOP
        self.huecos = []

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0

    def readQtable(self):
	"Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table

    def writeQtable(self):
	"Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")
        self.table_file.close()

    def computePosition(self, state):
	"""
	Compute the row of the qtable for a given state.
	Esto hay que cambiarlo ya que nuestra qtable es diferente a la del tutorial 4
	"""
        d = 0
        if state[5] == "East":
            d = 0
        elif state[5] == "West":
            d = 1
        elif state[5] == "North":
            d = 2
        else:
            d = 3
        return state[0]*64+state[1]*32+state[2]*16+state[3]*8+state[4]*4+d

    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.columAction[action]

        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
     	return max([self.getQValue(state, action) for action in self.actions])

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        acs = util.Counter()
        for action in self.actions:
			acs[action]=self.getQValue(state, action)
        return acs.argMax()

    def getPolicy(self, state):
	"Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state)

    def getValue(self, state):
	"Return the highest q value for a given state"
        return self.computeValueFromQValues(state)

    def getAc(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """

        # Pick Action
        flip = util.flipCoin(self.epsilon)

        if flip:
			return random.choice(self.actions)

        return self.getPolicy(state)

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        move = Directions.STOP
        LE=0
        self.legal = gameState.getLegalActions(0)
        self.legal.remove(Directions.STOP)

        state = self.generateState(gameState) #Aqui se debe generar el estado segun como lo hagamos
        move = self.getAc(state) #Accion a ejecutar desde ese estado, puede ser aleatoria con una probabilidad epsilon o elige la accion con un q value mayor
        for i in self.legal:
				if move== i:
					LE=1
        reward = self.getReward(state,move)
        if LE == 0:
            move=random.choice(self.legal)


        if self.lastState != None: #Si no se ha ejecutado al menos un estado pues no se hace update
			print "**************"+str(self.countActions)+"****************************"
			print "Estado tick:"+str(self.lastState)+"\n"
			print "Accion:"+str(move)+"\n"
			print "Estado tick siguiente:"+str(state)+"\n"
			print "Refuerzo:"+str(reward)+"\n"
			print "******************************************"
			self.update(self.lastState,self.move,state,self.reward) # Aqui realizamos el update, tras cada tick
        self.reward=reward
        self.lastState=state #Guardamos el estado anterior
        self.move=move
        return move

    def generateState(self, gameState):
        """
        Genarmos el estado compuesto por
           distGhost = distancia al fantasma mas cercano // 0 -> cerca (menos de 3 unidades), 1 -> medio (entre 3 y 7), 2 -> lejos (mas de 7 unidades)
           isParedEast = (0 -> no hay pared en la Direccion este, 1 -> hay pared)
           isParedWest
           isParedNorth
           isParedShouth
           directionGhost = direccion en la que se encunetra el fantasma mas cercano
        """
        state = [None, None, None, None, None, None]

        #Calculamos la distancia al fantasma mas cercano
        distGhosts = gameState.data.ghostDistances
        nearest = 100000
        for i in distGhosts:
            if i < nearest and i is not None:
                nearest = i
        if nearest <= 3:
            state[0] = 0
        elif nearest > 3 and nearest <= 7:
            state[0] = 1
        else:
            state[0] = 2

        legalActions = gameState.getLegalActions()
        #Calculamos los isPared
            #isParedEast
        if "East" in legalActions:
            state[1] = 0
        else:
            state[1] = 1

            #isParedWest
        if "West" in legalActions:
            state[2] = 0
        else:
            state[2] = 1

            #isParedNorth
        if "North" in legalActions:
            state[3] = 0
        else:
            state[3] = 1

            #isParedShouth
        if "South" in legalActions:
            state[4] = 0
        else:
            state[4] = 1

        #Bloque que controla si el pacman ha pasado por el hueco encontrado
        controlador =0
        x1,y1 = gameState.getPacmanPosition()
        if len(self.huecos)==2:
			if x1 ==self.huecos[0]:
				controlador=controlador+1
			if y1 ==self.huecos[1]:
				controlador=controlador+1
			if controlador == 2:
				self.huecos=[]

        posGhosts = gameState.getGhostPositions()
        nearestGhostIndex = distGhosts.index(nearest)
        nearestGhostPos = posGhosts[nearestGhostIndex]
        pacmanPosition = gameState.getPacmanPosition()

        print(self.huecos)
        if(len(self.huecos) == 2):
            goalPosition = self.huecos
        else:
            goalPosition = nearestGhostPos

        legales = []
        for a in self.goodActions(pacmanPosition,goalPosition): #Metodo goodActions devuelve las mejores acciones que puede realizar el pacman para llegar a su objetivo
            if a in legalActions:
                legales.append(a) #Buenas acciones legales
        if (len(legales) < 1):
            if (len(self.goodActions(pacmanPosition,goalPosition))): #Si existen buenas acciones pero no son legales es porque un muro esta impidiendo su ejecucion
                self.huecos = []
                rd= random.randint(0, len(self.goodActions(pacmanPosition,goalPosition))-1)
                self.buscaHueco(gameState,self.goodActions(pacmanPosition,goalPosition)[rd],pacmanPosition[0],pacmanPosition[1]) #Se busca hueco en una de las direcciones de las buenas acciones

        #Calculamos la direccion en la que se encuentra el fantasma o el hueco mas cercano
        #   esto lo hacemos calculando la distancia del fantasma al pacman y viendo cual es la componente mayor.
        #   Si es la X, la direccion sera o derecha o izquierda y dependera del sentido de esta. Con la Y parasria lo mismo
        relX = gameState.getPacmanPosition()[0] - goalPosition[0]
        relY = gameState.getPacmanPosition()[1] - goalPosition[1]

        if abs(relX) >= abs(relY):
            if relX > 0:
                state[5] = "West"
            elif relX < 0:
                state[5] = "East"
        elif abs(relY) > abs(relX):
            if relY > 0:
                state[5] = "South"
            elif relY < 0:
                state[5] = "North"


        return state

    def goodActions(self, pacmanPosition, goalPosition):
        axisY = pacmanPosition[1] - goalPosition[1]
        axisX = pacmanPosition[0] - goalPosition[0]
        acciones = []
        if (axisY < 0):
            acciones.append('North')
        elif (axisY > 0):
            acciones.append('South')
        if (axisX < 0):
            acciones.append('East')
        elif (axisX > 0):
            acciones.append('West')
        return acciones

    def buscaHueco(self,gameState,action,x_p,y_p):
        x=x_p
        y=y_p
        #Se evalua la coordenada a la que se llegaria con la accion pasada
        if (action=='East'):
            x=x+1
        elif (action=='West'):
			x=x-1
        elif (action=='North'):
			y=y+1
        else:
			y=y-1
        if y !=y_p: #El pacman se moveria a norte o sur
			xi = x
			xd = x-1
            #Bloque que evlua si existe un hueco en la horizontal de la posible coordenada y
			for i in range(0,gameState.getWalls().width-1):
				rd=random.randint(0,1)
				if rd == 0:
					if xi < gameState.getWalls().width:
						if gameState.getWalls()[xi][y] is False:
							self.huecos.append(xi)
							self.huecos.append(y)
							break
						xi=xi+1
					else:
						if xd > 0:
							if gameState.getWalls()[xd][y] is False:
								self.huecos.append(xd)
								self.huecos.append(y)
								break
							xd=xd-1

				else:
					if xd > 0:
						if gameState.getWalls()[xd][y] is False:
							self.huecos.append(xd)
							self.huecos.append(y)
							break
						xd=xd-1
					else:
						if xi < gameState.getWalls().width:
							if gameState.getWalls()[xi][y] is False:
								self.huecos.append(xi)
								self.huecos.append(y)
								break
							xi=xi+1
        else: #El pacman se moveria a este o oeste
			yi = y
			yd = y-1
            #Bloque que evlua si existe un hueco en la vertical de la posible coordenada x
			for i in range(0,gameState.getWalls().height-3):
				rd=random.randint(0,1)
				if rd == 0:
					if yi < gameState.getWalls().height:
						if gameState.getWalls()[x][yi] is False:
							self.huecos.append(x)
							self.huecos.append(yi)
							break
						yi=yi+1
					else:
						if yd > 2:
							if gameState.getWalls()[x][yd] is False:
								self.huecos.append(x)
								self.huecos.append(yd)
								break
							yd=yd-1
				else:
					if yd > 2:
							if gameState.getWalls()[x][yd] is False:
								self.huecos.append(x)
								self.huecos.append(yd)
								break
							yd=yd-1
					else:
						if yi < gameState.getWalls().height:
							if gameState.getWalls()[x][yi] is False:
								self.huecos.append(x)
								self.huecos.append(yi)
								break
							yi=yi+1
        return self.huecos

    def getReward(self, state, move):
        reward = 0
        #
        # Para el caso de fantasmas a menos de 3 unidades
        #
        if state[0] == 0:
            if state[5] == "North":
                if state[3] == 1 and move == "North":
                    reward = -15
                elif state[3] == 1 and move == "East":
                    reward = 15
                elif state[3] == 1 and move == "West":
                    reward = 15
                elif state[3] == 1 and move == "South":
                    reward = -50
                elif state[3] == 0 and move == "North":
                    reward = 50
                elif state[3] == 0 and move is not "North":
                    reward = -50
            elif state[5] == "East":
                if state[1] == 1 and move == "North":
                    reward = 15
                elif state[1] == 1 and move == "East":
                    reward = -15
                elif state[1] == 1 and move == "West":
                    reward = -50
                elif state[1] == 1 and move == "South":
                    reward = 15
                elif state[1] == 0 and move == "East":
                    reward = 50
                elif state[1] == 0 and move is not "East":
                    reward = -50
            elif state[5] == "West":
                if state[2] == 1 and move == "North":
                    reward = 15
                elif state[2] == 1 and move == "East":
                    reward = -50
                elif state[2] == 1 and move == "West":
                    reward = -15
                elif state[2] == 1 and move == "South":
                    reward = 15
                elif state[2] == 0 and move == "West":
                    reward = 50
                elif state[2] == 0 and move is not "West":
                    reward = -50
            if state[5] == "South":
                if state[4] == 1 and move == "North":
                    reward = -50
                elif state[4] == 1 and move == "East":
                    reward = 15
                elif state[4] == 1 and move == "West":
                    reward = 15
                elif state[4] == 1 and move == "South":
                    reward = -15
                elif state[4] == 0 and move == "South":
                    reward = 50
                elif state[4] == 0 and move is not "South":
                    reward = -50
        #
        # Para el caso de fantasmas a una distancia entre 3 y 7 unidades
        #
        elif state[0] == 1:
            if state[5] == "North":
                if state[3] == 1 and move == "North":
                    reward = -10
                elif state[3] == 1 and move == "East":
                    reward = 10
                elif state[3] == 1 and move == "West":
                    reward = 10
                elif state[3] == 1 and move == "South":
                    reward = -25
                elif state[3] == 0 and move == "North":
                    reward = 25
                elif state[3] == 0 and move is not "North":
                    reward = -25
            elif state[5] == "East":
                if state[1] == 1 and move == "North":
                    reward = 10
                elif state[1] == 1 and move == "East":
                    reward = -10
                elif state[1] == 1 and move == "West":
                    reward = -25
                elif state[1] == 1 and move == "South":
                    reward = 10
                elif state[1] == 0 and move == "East":
                    reward = 25
                elif state[1] == 0 and move is not "East":
                    reward = -25
            elif state[5] == "West":
                if state[2] == 1 and move == "North":
                    reward = 10
                elif state[2] == 1 and move == "East":
                    reward = -25
                elif state[2] == 1 and move == "West":
                    reward = -10
                elif state[2] == 1 and move == "South":
                    reward = 10
                elif state[2] == 0 and move == "West":
                    reward = 25
                elif state[2] == 0 and move is not "West":
                    reward = -25
            if state[5] == "South":
                if state[4] == 1 and move == "North":
                    reward = -25
                elif state[4] == 1 and move == "East":
                    reward = 10
                elif state[4] == 1 and move == "West":
                    reward = 10
                elif state[4] == 1 and move == "South":
                    reward = -10
                elif state[4] == 0 and move == "South":
                    reward = 25
                elif state[4] == 0 and move is not "South":
                    reward = -25
        #
        # Para el caso de fantasmas a una distancia mayor de 7 unidades
        #
        elif state[0] == 2:
            if state[5] == "North":
                if state[3] == 1 and move == "North":
                    reward = -5
                elif state[3] == 1 and move == "East":
                    reward = 5
                elif state[3] == 1 and move == "West":
                    reward = 5
                elif state[3] == 1 and move == "South":
                    reward = -15
                elif state[3] == 0 and move == "North":
                    reward = 15
                elif state[3] == 0 and move is not "North":
                    reward = -15
            elif state[5] == "East":
                if state[1] == 1 and move == "North":
                    reward = 5
                elif state[1] == 1 and move == "East":
                    reward = -5
                elif state[1] == 1 and move == "West":
                    reward = -15
                elif state[1] == 1 and move == "South":
                    reward = 5
                elif state[1] == 0 and move == "East":
                    reward = 15
                elif state[1] == 0 and move is not "East":
                    reward = -15
            elif state[5] == "West":
                if state[2] == 1 and move == "North":
                    reward = 5
                elif state[2] == 1 and move == "East":
                    reward = -15
                elif state[2] == 1 and move == "West":
                    reward = -5
                elif state[2] == 1 and move == "South":
                    reward = 5
                elif state[2] == 0 and move == "West":
                    reward = 15
                elif state[2] == 0 and move is not "West":
                    reward = -15
            if state[5] == "South":
                if state[4] == 1 and move == "North":
                    reward = -15
                elif state[4] == 1 and move == "East":
                    reward = 5
                elif state[4] == 1 and move == "West":
                    reward = 5
                elif state[4] == 1 and move == "South":
                    reward = -5
                elif state[4] == 0 and move == "South":
                    reward = 15
                elif state[4] == 0 and move is not "South":
                    reward = -15
        return reward

    def update(self, state, action, nextState, reward):
        id_a=self.computePosition(state)
        l=self.columAction[action]
        self.q_table[id_a][l]=(1-self.alpha)*self.q_table[id_a][l]+self.alpha * (reward+self.discount * self.getValue(nextState))
