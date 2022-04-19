# Simulation of 1D Freezing Temperature 1 Tile Automata by David C.
# Modified to CFG Tile Automata by Sonya C. 4/15/2022


from collections import defaultdict
import re # used to find substring matches

# takes in cfg.txt and makes rules into dictionary 
cfgDict = {}
symbols = 0
with open ('CFG.txt') as f:

	for line in f:
		if symbols == 0:
			symbols = line.split()
			print(symbols)
		else:
			(key, val) = line.split()
			cfgDict[(key)] = val

	for k in cfgDict.keys():
		print(k, cfgDict[k])

# split keys and values into different lists 
# split values into left and right side
	valueList = []
	for v in cfgDict.values():
		valueList .append( list(v))
		print(list(v))
		

		
		
# capital letters - nonterminals 
# lowercase - termimals



class oneDFreezTemp1TA():


	def __init__(self, states, initStates, affinities, transitions):
		self.states = states
		self.initStates = initStates
		self.affinities = affinities
		self.transitions = transitions

		# affinityMap is a dictionary mapping states to the states they hav affinity with
		# on either the right or left side
		# Example:
		#	states = {A,B,C}
		# 	affinities = ((A,B)(B,C)
		#	affinityMap = {A : {	"l": set(), 
		#							"r": B
		#						}
		#				   } etc ...
		#
		self.affinityMap = defaultdict(lambda: {"l": set(), "r": set()})


		# transitionMap is a dictionary mapping states to transitions that include 
		# that state
		self.transitionMap = defaultdict(set)

		self.linkStatesToAffinities(self.states, self.affinities, self.affinityMap)
		self.linkTransitionsToAffinities(self.states, self.transitions, self.transitionMap)

		self.producibles = set()
		self.producibles.update(self.initStates)

		self.nonterminals = defaultdict(lambda: 0)

	# Takes a set of states and a set of affinities and maps states to affinities that
	# they are included in
	def linkStatesToAffinities(self, states, affinities, affinityMap):
		
		for state in states:
			for affinity in affinities:
				if state == affinity[0]:
					self.affinityMap[state]["r"].add(affinity[1])
				if state == affinity[1]:
					self.affinityMap[state]["l"].add(affinity[0])


	# Takes a set of states and a set of transitions and maps states to transitions that
	# they are included in
	def linkTransitionsToAffinities(self, states, transitions, transitionMap):
		
		for state in states:
			for transition in transitions:
				for s in (transition[0][0], transition[0][1]):
					if s == state: transitionMap[state].add(transition)


	def getNewProducibles(self):

		
		newProds = set()
		# Get new producibles through 3 different methods: Attachment, transition, detachment
  
		for newProducibles in (self.getNewProduciblesByAttachment(self.producibles, self.affinityMap),
								self.getNewProduciblesByTransition(self.producibles, self.transitions)):
								#self.getNewProduciblesByDetachment(self.producibles, self.affinities)):
		
			newProds.update(newProducibles)
		
		self.producibles.update(newProds)
	
	
	def getTerminals(self):
		return self.findTerminalAssemblies(self.producibles, self.nonterminals)


	# Takes a set of 1D assemblies, checks if any of them can attach to each other
	def getNewProduciblesByAttachment(self, producibles, affinityMap):

		newProducibles = set()

		# For every pair of producibles
		for producibleA in producibles:
			for producibleB in producibles:


				leftStateA = producibleA[0:2] 
				#lenA = len(producibleA)
				rightStateA = producibleA[-2:]
				#print(leftStateA, rightStateA)
				newTempList = [] # Holds new producibles to be added to the set

				# Check if A can attach to the right of B
				#lenB = len(producibleB)
				if producibleB[-2:] in affinityMap[leftStateA]["l"]:
					newTempList.append(producibleB + producibleA)
				if producibleB[0:2] in affinityMap[rightStateA]["r"]:
					newTempList.append(producibleA + producibleB)

				# Check if B can attach to the right of A
				for newProd in newTempList:
					self.nonterminals[producibleA] = 1 # Mark the assemblies as non terminal since they qualified for an attachment
					self.nonterminals[producibleB] = 1
					if newProd not in producibles:
						newProducibles.add(newProd)

		return newProducibles

	# Takes a set of 1D assemblies, and a set of transitions, and returns new assembies that can be produced
	def getNewProduciblesByTransition(self, producibles, transitions):

		newProducibles = set()

		# For every producible/transition pair
		for producible in producibles:	

			if len(producible) == 1: continue
			for transition in transitions:

				# Check if the pair of states needed for the transition to occur 
				transitionString = transition[0][0] + transition[0][1]
				afterTransitionString = transition[1][0] + transition[1][1]

				# Find all occurences of the transition substring
				occurences = [m.start() for m in re.finditer('(?='+transitionString+')', producible)]
				
				# Mark this producible as non terminal since it qualified for a state transition
				if len(occurences) > 0:
					self.nonterminals[producible] = 1
				for occurence in occurences:
					newProducible = producible[:occurence] + afterTransitionString + producible[occurence+4:]
					if newProducible not in producibles:
						newProducibles.add(newProducible)

		return newProducibles


	# Takes a set of 1D assemblies, and a set of affinities, and checks if the assemblies can be detached into two separate assemblies
	def getNewProduciblesByDetachment(self, producibles, affinities):

		newProducibles = set()

		# For every adjacent pair of states in a producible
		for producible in producibles:
			for x in range(len(producible)-1):
				subString = producible[x] + producible[x + 1]
				if (producible[x], producible[x+1]) not in affinities:
					self.nonterminals[producible] = 1 # Mark assembly as non terminal since it qualified for a detachment

					# Check if the two subassemblies created by detachment are new, if so add them to the set of new producibles
					for subAssembly in (producible[:x+1], producible[x+1:]):
						if subAssembly not in producibles:
							newProducibles.add(subAssembly)

		return newProducibles

	# Takes in a set of producibles and a dictionary marking certain producibles as non terminal, returns every producible that is not terminal
	def findTerminalAssemblies(self, producibles, nonterminals):

		terminals = set()
		for producible in producibles:
			if nonterminals[producible] == 0:
				terminals.add(producible)

		return terminals






# states = {'1','A','2','B','3','C'}
# initStates = {'1','A'}
# affinities = {('1','A'),('1','2'),('B','A'),('2','B'),('3','C'),('3','A'),('1','C'),('C', 'B'),('2','3'),('3','3'),('C','C')}
# transitions = {(('1','A'),('1','2')),  (('1','A'),('B','A')),  (('3','A'),('3','3')),  (('1','C'),('C','C')),  (('2','B'),('2','3')),  (('2','B'),('C','B'))}


states = []
initStates = []

# Make states
# all states- get all characters from keys in cfg dict except duplicates if any
# from value list get characters that arent included in keys from cfg dict

for t in symbols[0]:
	states.append("L" + t)
	states.append("R" + t)
	#initStates.append("L" + t)
	#initStates.append("R" + t)

for nt in symbols[1]:
	states.append(nt)
	

affinities = []
transitions = []
#= {('1','A'),('1','2'),('B','A'),('2','B'),('2','5'),('5','1'),('1','E'),('E','B'),('5','3'),('C','E'),('3','C'),('3','6'),('6','E'),('6','6'),('6','B'),('6','A'),('6','4'),('F','C'),('5','F'),('2','F'),('1','F'),('D','F'),('4','D')}

ruleAppear = {}

for letter in symbols[1]:
	ruleAppear[letter] = {"L":0, "R":0}

#print(ruleAppear)

#loop through the cfg rules in cfgDict
for rule in valueList:
	# Get the first state
	# If it's a terminal
	state1 = "0"
	if rule[0].islower(): 
		state1 = "L" + rule[0]
		initStates.append("L" + rule[0])
	if rule[0].isupper():
		# Keep track of what sides rules appear on
		ruleAppear[rule[0]]["L"] = 1

		# get color of sticky state
		t = rule[0]
		while t.isupper():
			t = cfgDict[t][1]

		state1 = rule[0] + t

	state2 = "0"
	if rule[1].islower():
		state2 = "R" + rule[1]
		initStates.append("R" + rule[1])
	if rule[1].isupper():
		# Keep track of what sides rules appear on
		ruleAppear[rule[1]]["R"] = 1

		# Get color of sticky state
		t = rule[1]
		while t.isupper():
			t = cfgDict[t][0]

		state2 = rule[1] + t

	affinities.append((state1, state2))

for sym in cfgDict.keys():
	# print(symbol, "->", cfgDict[symbol][0], cfgDict[symbol][1])
	# Get start states

	rule = cfgDict[sym]

	state1 = "0"
	if rule[0].islower(): 
		state1 = "L" + rule[0]
		initStates.append("L" + rule[0])
	if rule[0].isupper():
		# Keep track of what sides rules appear on
		ruleAppear[rule[0]]["L"] = 1

		# get color of sticky state
		t = rule[0]
		while t.isupper():
			t = cfgDict[t][1]

		state1 = rule[0] + t

	state2 = "0"
	if rule[1].islower():
		state2 = "R" + rule[1]
		initStates.append("R" + rule[1])
	if rule[1].isupper():
		# Keep track of what sides rules appear on
		ruleAppear[rule[1]]["R"] = 1

		# Get color of sticky state
		t = rule[1]
		while t.isupper():
			t = cfgDict[t][0]

		state2 = rule[1] + t

	newState1 = state1
	newState2 = state2

	if ruleAppear[sym]["L"] == 1:
		# Add Transition Rule
		print(sym, "appears left")

		# Rule appears on left, means we need right type of assembly (ie assembly with right affinity or "glue")
		# The state must first walk to the left side to change all the middle states to the right symbol
		newState1 = sym + state1[1]

		transitions.append(((state1, state2), (newState1, state2)))

	if ruleAppear[sym]["R"] == 1:
		# Add Transition Rule
		print(sym, "appears right")

		# reverse from above
		newState2 = sym + state2[1]

		transitions.append(((state1, state2), (state1, newState2)))

	





#{(('D','E'),('D','F')),  (('A','B'),('G','B')) }

# make TR


states = set(states)
initStates = set(initStates)
affinities = set(affinities)

simulation = oneDFreezTemp1TA(states, initStates, affinities, transitions)
print("States: ", states)
print("Initial States: ", initStates)
print("Affinities: ", affinities)
print("Transitions: ", transitions)


print("Stage ", 0, "Producibles: \n", simulation.producibles, "\n\n\n")
x=0
size, newSize = -1,0
while size != newSize and x < 5:
	x+=1
	size = len(simulation.producibles)
	simulation.getNewProducibles()
	print("Stage ", x, "Producibles: \n", simulation.producibles, "\n\n\n")
	newSize = len(simulation.producibles)

print("Terminals: ", simulation.getTerminals())


for t in simulation.getTerminals():
	print(t[-2:])