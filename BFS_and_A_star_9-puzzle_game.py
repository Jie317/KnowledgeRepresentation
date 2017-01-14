# coding: utf-8 
import json
import numpy 
import math
import argparse
from random import shuffle

def BFS_jeu_Taquin(e_init, e_sol, graph=None, get_graph = False):
	''' Can be used either to generate the graph or to search the path '''
	if not get_graph: 
		check_resolvable(e_init, graph)
		if e_init == e_sol: 
			print 'BFS finds solution of 0 step(s) when visited 0 states.'
			return
		print '\nStarting BFS search...'
	if get_graph: 
		e_init = '123456789'
		print 'Starting graph generation...'
	store_graph = {}
	queue = []
	pred = {}
	queue.append(e_init)
	E_star = [e_sol]
	visited = set()
	count = 0
	end = False
	while queue and not end:
		e = queue.pop(0)
		visited.add(e)
		E_e, all_next_etats = unvisited_transmissions(e, visited, graph, get_graph)
		if get_graph: store_graph[e] = all_next_etats
		for c in E_e:
			if c not in queue: queue.append(c)
			pred[c] = e
			if (not get_graph) and (c in E_star): 
				end = True
				reconstruct_path(pred, c, 'BFS', count)
			if count%20000 == 0: print 'States visited: %d\t...' % count
			count += 1
	if get_graph: 
		fname = 'graph_Taquin_even.txt'
		json.dump(store_graph, open(fname,'w'),indent=1)
		print 'Graph generated and stored in %s' % fname

def A_star_Taquin(start, goal, graph):
	check_resolvable(start, graph)
	print '\nStarting A-star search...'
	processed = set()
	ongoing = set ()
	ongoing.add(start)
	fCost = {}
	lowestCostTo = {}
	lowestCostTo[start] = 0
	fCost[start] = h_Taquin(start, goal)
	bestPrevious = {}
	count = 0
	end = False
	while ongoing and not end:
		bestNode = min(ongoing, key=lambda x:fCost[x]) # or min(ongoing, key=fCost.get)
		if bestNode == goal:
			reconstruct_path(bestPrevious, bestNode, 'A-star', count)
			end = True
		processed.add(bestNode)
		ongoing.remove(bestNode)
		for n in unvisited_transmissions(bestNode, processed, graph)[0]:
			new_cost_to_n = lowestCostTo[bestNode] + 1 # cost(current, next) = 1
			if n not in ongoing: ongoing.add(n)
			elif new_cost_to_n >= lowestCostTo[n]: continue # use 'else if' to assure that the n exists
			lowestCostTo[n] = new_cost_to_n
			bestPrevious[n] = bestNode
			fCost[n] = lowestCostTo[n] + h_Taquin(n, goal)
			if count%5000==0: print 'States visited: %d\t...' % count
			count += 1


def unvisited_transmissions(e, visited, graph=None, get_graph=False): # return the next possible and unvisited states
	store_etats = [] # get all new states even some of them are already visited
	new_etats = [] # possible and unvisited transmissions
	if get_graph:
		pos = e.index('9') # get the position of '9'
		x,y = divmod(pos, 3)
		newpos = []  
		if y < 2: newpos.append(pos+1)  
		if y > 0: newpos.append(pos-1)  
		if x < 2: newpos.append(pos+3)  
		if x > 0: newpos.append(pos-3)  
		for ipos in newpos:  
			tmp = list(e)
			tmp[ipos] = '9'
			tmp[pos] = e[ipos]
			tmp = ''.join(tmp)
			if get_graph: store_etats.append(tmp)
			if tmp not in visited: new_etats.append(tmp)
	if graph:
		for el in graph[e]:
			if el not in visited: new_etats.append(el)
	return new_etats, store_etats

def h_Taquin(current, e_sol): # get heuristic by the sum of Manhattan distance
	sum_distance = 0
	for v in e_sol:
		p_sol = divmod(e_sol.index(v), 3)
		p_cur = divmod(current.index(v), 3)
		sum_distance += abs(p_cur[0]-p_sol[0]) + abs(p_cur[1]-p_sol[1])
	return sum_distance

def reconstruct_path(cameFrom, n, name, count): # return the shortest path to the goal state
	total_path = [n]
	while n in cameFrom:
		n = cameFrom[n]
		total_path.append(n)
	total_path.reverse()
	print '%s finds solution of %s step(s) when visited %d states: %s\n' % (name, len(total_path)-1, count, ' -> '.join(total_path))
	
def check_resolvable(e_init, graph):
	if e_init not in graph:
		print '\nCan not find solution for the state: %s. Please choose another state to start! \n' % e_init
		print '\nEnd of the project <<<<<<'
		exit()



def main():
	parser = argparse.ArgumentParser(description='A script to find the best solution of the game Taquin by applying two search algorithms on its state graph: BFS and A-star. The states are represented by strings such as \'123456789\'. The goal state is defined as 123456789 where 9 is the empty square.')
	parser.add_argument('-g', action='store_true', help='generate and store the state graph of Taquin')
	parser.add_argument('-i', type=str, help='initial state (a random sequence will be generated if not given)')
	parser.add_argument('-a', action='store_true', help='apply A-star search algorithm')
	parser.add_argument('-b', action='store_true', help='apply BFS search algorithm')
	parsed = parser.parse_args()
	if not any(vars(parsed).values()): parser.error("At least one of -a or -b must be given")


	if parsed.g: BFS_jeu_Taquin(Taquin_init, e_sol, get_graph=True) # generate the graph

	try: # load the graph as dictionary
		graph = json.load(open("graph_Taquin_even.txt")) 
		print 'Number of states in Taquin graph: %d' % len(graph)
	except:
		print 'No state graph file found, please add \'-g\' to generate the graph.'

	e_sol = '123456789' # the goal state
	if not parsed.i:
		Taquin_init = [i for i in xrange(1,10)] # 9 is the blank square
		shuffle(Taquin_init) # generate a random initial state
		Taquin_init = ''.join(map(str,Taquin_init)) # convert it to String type
	else: Taquin_init = parsed.i# set a manual initial state

	print 'Initial Taquin state: %s %s' % (Taquin_init, '(randomly generated)' if not parsed.i else ' ')


	



	if parsed.a: A_star_Taquin(Taquin_init, e_sol, graph) # start A-star search

	if parsed.b: BFS_jeu_Taquin(Taquin_init, e_sol, graph) # start BFS search


if __name__ == '__main__':
	main()

