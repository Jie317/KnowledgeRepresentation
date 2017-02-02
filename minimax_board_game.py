import copy
import argparse
import numpy as np

'''
An application of minimax in a board game. Minimax algorithm needs to well define the heuristic value for each state. We have tried several methods to evaluate the state and finally chosen the combination of some of them. After tuning the parameters in these methods, we get a performance that seems reasonable and intelligble. Besides, we have developed several features to dynamically adjust the depth and the intensity of the search to speed up the calculation or break the deadlock. 

Game introduction:
A board game where two troops attack each other until all the opponent resources disappear. The resource S and R can move one squares while L can move two squares each time at any of the four directions. The attack range of each resource is defined in the attack_range function. In each turn, the player can move and attack once. The resource disappears once being attacked.

If you want to develop this script, please focus on tuning the parameters or developing new state evaluation methods in the heuristic function.
'''

def minimax_decision(depth, board, player=None, get_action=False, step=None): 
	# apply the minimax and return its action (a matrix as the new board)
	if get_action: 
		print '------------------------------------------------\nGlobal step: %d\tSearch depth: %d\
				\nPlayer %s (%s) is calculating...' % (step, depth, player, 'lowercase' 
				if player=='p1' else 'uppercase')

	global count_minimax, current_player, no_adjust
	count_minimax += 1

	if depth == 0: # when reaching the last search layer
		return heuristic(board, current_player)

	action = board # in case that no action can be taken
	auto_adjust = lambda x: 3 if len(x)>=20 else 2 if len(x)>=10 else 1 # adjust search intensity
	if player == 'p1': # for maximizing player (player 1)
		best_value = -1e500	
		sub_states = transmissions(board, 'p1')
		#if get_action: print 'Possible actions: %d' % len(sub_states)
		for child in sub_states[::auto_adjust(sub_states) if not no_adjust else 1]:
			value = minimax_decision(depth-1, child, 'p2')
			if best_value < value:
				best_value = value
				if get_action: action = child
		if get_action: return action
		return best_value

	else: # for minimizing player
		best_value = +1e500
		sub_states = transmissions(board, 'p2')
		#if get_action: print 'Possible actions: %d' % len(sub_states)
		for child in sub_states[::auto_adjust(sub_states) if not no_adjust else 1]:
			value = minimax_decision(depth-1, child, 'p1')
			if best_value > value:
				best_value = value
				if get_action: action = child
		if get_action: return action
		return best_value
	
def heuristic(board, current_player): # for player 1 (lowercase)
	h = 0 # heuristic value
	value_dict = {'l': 5000, 's': 15000, 'r': 8000, 'L': 5000, 'S': 15000, 'R': 8000}
	so_me = resources_player_1 if current_player=='p1' else resources_player_2
	so_op = resources_player_2 if current_player=='p1' else resources_player_1
	# get my resource positions
	poss_me = {} # the key is the resource name, and the value is the position list
	poss_me_list = []
	poss_me[so_me[0]] = pos_list(so_me[0], board)
	poss_me[so_me[1]] = pos_list(so_me[1], board)
	poss_me[so_me[2]] = pos_list(so_me[2], board)
	for k in poss_me: poss_me_list += poss_me[k]
	# get opponent's resource positions
	poss_op = {}
	poss_op_list = []
	poss_op[so_op[0]] = pos_list(so_op[0], board)
	poss_op[so_op[1]] = pos_list(so_op[1], board)
	poss_op[so_op[2]] = pos_list(so_op[2], board)
	for k in poss_op: poss_op_list += poss_op[k]

	# The heuristic value consists of the following 4 parts

	# 1. check win or lose
	if len(poss_me_list)==0: return -1e6
	if len(poss_op_list)==0: return +1e6

	# 2.1 calculate the total minimal distance between the two troops
	dists_mo = []
	for p in poss_me_list:
		dists = []
		for pp in poss_op_list: 
			ab = abs(p[0]-pp[0]) + abs(p[1]-pp[1])  # Manhattan distance
			# 2.2 calculate the total distance between the two troops
			#h -= ab 
			dists.append(ab)
		h -= min(dists) * value_dict[board[p[0]][p[1]]] / 100
	#	dists_mo.append(min(dists))

	# 2.3 calulate the variance of the minimal distances between two troops 
	# h -= np.var(dists_mo) * 10 * abs(len(poss_me_list) - len(poss_op_list))# variance

	# 2.4 calculate the total inner distance among its own troop
	# dists_mm = []
	# for p in poss_me_list:
	# 	dists = []
	# 	for pp in poss_me_list: 
	# 		ab = abs(p[0]-pp[0]) + abs(p[1]-pp[1])
	# 		h -= ab * 0.2

	# 3. caculate how much exposed in the attack range of the opponent
	attack_range_op = whole_attack_range(poss_op, board)
	for so in poss_me:
		for pos in poss_me[so]: 
			if pos in attack_range_op: h -= value_dict[so]

	# 4. caculate the firepower of the two troops
	for so in so_me: h += len(poss_me[so]) * value_dict[so]
	for so in so_op: h -= len(poss_op[so]) * value_dict[so]
	
	return h if current_player=='p1' else -h

def transmissions(board, p): # return all the possible states in this step
	def remove_duplicates(lst):
		new_list = set()
		new_states = []
		for s in lst: new_list.add('\n'.join('\t'.join(r) for r in s))
		for s in new_list: new_states.append([i.split('\t') for i in s.split('\n')])
		return new_states

	new_states = []
	for so in (resources_player_1 if p=='p1' else resources_player_2):
		for pos in pos_list(so, board): # find all new states for each resource
			new_states += move_then_attack(pos, so, board)
			new_states += attack_then_move(pos, so, board)

	return remove_duplicates(new_states)

def attack_then_move(position, resource, board): 
	# return all possible states when attacking firstly (if there are reachable targets)
	s_new_states = [] # new states for the resource
	for state in attack(board, resource, position):
		s_new_states += move_then_attack(position, resource, board, _attack=False)
	
	return s_new_states

def move_then_attack(position, resource, board, _attack=True): 
	# return all possible states for the resource when moving firstly
	s_new_states = [] # new states for the resource
	x = position[0]
	y = position[1]
	ss = 1 # step size
	if resource == 'l' or resource == 'L': ss = 2
	if x+ss >= 0 and x+ss <= 24:
		if board[x+ss][y] == ' ' and board[x+1][y] == ' ':
			b_copy = copy.deepcopy(board)
			b_copy[x+ss][y] = resource
			b_copy[x][y] = ' '
			if _attack: s_new_states += attack(b_copy, resource, [x+ss, y]) # possible attacks
			s_new_states.append(b_copy) # don't attack, just take a move
	if x-ss >= 0 and x-ss <= 24:
		if board[x-ss][y] == ' ' and board[x-1][y] == ' ':
			b_copy = copy.deepcopy(board)
			b_copy[x-ss][y] = resource
			b_copy[x][y] = ' '
			if _attack: s_new_states += attack(b_copy, resource, [x-ss, y]) # possible attacks
			s_new_states.append(b_copy) # don't attack, just take a move
	if y+ss >= 0 and y+ss <= 24:
		if board[x][y+ss] == ' ' and board[x][y+1] == ' ':
			b_copy = copy.deepcopy(board)
			b_copy[x][y+ss] = resource
			b_copy[x][y] = ' '
			if _attack: s_new_states += attack(b_copy, resource, [x, y+ss]) # possible attacks
			s_new_states.append(b_copy) # don't attack, just take a move
	if y-ss >= 0 and y-ss <= 24:
		if board[x][y-ss] == ' ' and board[x][y-1] == ' ':
			b_copy = copy.deepcopy(board)
			b_copy[x][y-ss] = resource
			b_copy[x][y] = ' '
			if _attack: s_new_states += attack(b_copy, resource, [x, y-ss]) # possible attacks
			s_new_states.append(b_copy) # don't attack, just take a move
	
	return s_new_states

def whole_attack_range(poss_op, board):
	whole_attack_range = []
	for so in poss_op:
		for pos in poss_op[so]: 
			whole_attack_range += attack_range(board, so, pos)
	
	return whole_attack_range

def attack_range(board, resource, pos):# return the squares attackable by the resource
	x = pos[0]
	y = pos[1]
	if resource == 'l': 
		squares_reachable = [[x+1, y], [x, y+1], [x, y-1]]
	if resource == 'r':
		squares_reachable = [[x+1, y], [x+2, y], [x+3, y], 
							[x, y+1], [x, y+2], [x, y-1], [x, y-2]]
	if resource == 's' or resource == 'S':
		squares_reachable = [[x+1, y], [x+2, y],[x-1, y], [x-2, y],
							[x, y-1], [x, y-2],[x, y+1], [x, y+2],
							[x+1, y+1], [x+2, y+2],[x-1, y+1], [x-2, y+2],
							[x-1, y-1], [x-2, y-2],[x+1, y-1], [x+2, y-2]]
	if resource == 'L':
		squares_reachable = [[x-1, y], [x, y+1], [x, y-1]]
	if resource == 'R':
		squares_reachable = [[x-1, y], [x-2, y], [x-3, y], 
							[x, y+1], [x, y+2], [x, y-1], [x, y-2]]
	
	return squares_reachable

def attack(board, resource, pos): # return all possible attacks from the move
	sub_states = []
	# detect player and get opponent resource positions
	opponent_resources = positions_all('p2' if resource.islower() else 'p1', board)
	# find possible targets to attack
	for p in opponent_resources:
		if p in attack_range(board, resource, pos):
			b_copy = copy.deepcopy(board)
			b_copy[p[0]][p[1]] = ' ' # remove the opponent resource
			sub_states.append(b_copy) # new possible transmissions
	return [board] if len(sub_states) == 0 else sub_states 

def positions_all(p, board):
	all_pos = []
	for s in (resources_player_1 if p=='p1' else resources_player_2):
		all_pos += pos_list(s, board)
	return all_pos

def pos_list(s, board): # find the position list of a type of resource in the board
	poss = []
	for x in xrange(25):
		for y in xrange(25):
			if board[x][y] == s: poss.append([x, y])

	return poss

def init_board():
	global resources_player_1, resources_player_2
	resources_player_1 = ['s', 'l', 'r']
	resources_player_2 = ['S', 'L', 'R']
	board = [[' ' for r in xrange(25)] for c in xrange(25)] 
	board[2][5] = 'S'
	board[2][8] = 'S'
	board[2][12] = 'S'
	board[2][16] = 'S' 
	board[2][19] = 'S'
	board[3][3] = 'R'
	board[3][21] = 'R'
	board[5][2] = 'R'
	board[5][22] = 'R'
	board[4][5:21:2] = 'L' * 8
	board[5][10:16:2] = 'L' *3	
	board[19][10:16:2] = 'l' *3	
	board[22][5] = 's'
	board[22][8] = 's'
	board[22][12] = 's'
	board[22][16] = 's' 
	board[22][19] = 's'
	board[21][3] = 'r'
	board[21][21] = 'r'
	board[19][2] = 'r'
	board[19][22] = 'r'
	board[20][5:21:2] = 'l' * 8
	
	return board

def print_board(b, step, init=False, depth=5):
	if b==None: return
	if init: print "\n------------------------------------------------\
				\nGame starts... Search depth: %d" % depth
	if not init: 
		print '>>> Player %d (%s) has moved.' % (1 if step%2==1 else 2, 
					'lowercase' if step%2==1 else 'uppercase')
		print 'Total iterations on minimax_decision(): %d' % count_minimax
	print '\n%s\n' % ('\n'.join('|%s|' % '|'.join(r) for r in b))

def check_win(b):
	if len(positions_all('p1',b)) == 0 :
		print 'Player 1 has won. Game ended.'
		exit()
	if len(positions_all('p2',b)) == 0 :
		print 'Player 2 has won. Game ended.'
		exit()

def player_2_human(b, fired=False, moved=False):
	global step
	b_copy = copy.deepcopy(b)
	action = raw_input("Enter your action by inputing one position to attack or two positions \
to move a resource:Such as: [3,6] or [3,5],[6,7] or 'n' to skip (The board is represented as a matrix\
, so the square in the top left corner is (0,0))\n")
	if action=='n': return b
	action = '[%s]' % action
	try: a = eval(action)
	except:
		print 'Please check the format and try again.'
		return player_2_human(b)
	fired = False
	moved = False
	if len(a) == 1 and not fired: # fire
		if b_copy[a[0][0]][a[0][1]].islower(): 
			b_copy[a[0][0]][a[0][1]] = ' '
			if b_copy in transmissions(b, 'p2'): 
				fired = True
				print_board(b_copy, step)
				if raw_input('Then move? (\'n\' to skip)') != 'n':
					return player_2_human(b_copy, fired=True)
				else:  return b_copy
			else:
				if raw_input('Wrong input. Try again? (y/n)') == 'y': 
					return player_2_human(b)
	elif len(a) == 2 and not moved: # move
		if b_copy[a[0][0]][a[0][1]].isupper(): 
			temp = b_copy[a[0][0]][a[0][1]]
			b_copy[a[0][0]][a[0][1]] = ' '
			b_copy[a[1][0]][a[1][1]] = temp
			if b_copy in transmissions(b, 'p2'): 
				moved = True
				print_board(b_copy, step)
				if raw_input('Then attack? (\'n\' to skip)') != 'n':
					return player_2_human(b_copy, moved=True)
				else:  return b_copy
			else:
				if raw_input('Wrong input. Try again? (y/n)') == 'y': 
					return player_2_human(b)
	else: print 'Wrong action!'



def main():
	parser = argparse.ArgumentParser(description='A script to play the game by minimax algorithm.')
	parser.add_argument('-d', type=int, help='set search depth in minimax, 2 by default', default=2)
	parser.add_argument('-c', action='store_true', help='close dynamic adjustment on search depth and intensity')
	parser.add_argument('-u', action='store_true', help='play with human (without this parameter the computer will play with itself)')
	parser.add_argument('-t', type=float, 
		help='threshold number of iterations on minimax search ( * 1e6). Default value is 100 * 1e6', default=100)
	parsed = parser.parse_args()

	global count_minimax, current_player, no_adjust, step
	step = 0
	count_minimax = 0
	search_depth = parsed.d
	deepen_1 = not parsed.c
	deepen_2 = not parsed.c
	no_adjust = parsed.c
	threshold = parsed.t*1e6
	human = parsed.u
	states_cache = ['' for i in xrange(10)] # check deadlock
	board_updated = init_board() # initiate the board
	print_board(board_updated, 0, init=True, depth=parsed.d)
	while (True):
		# player 1's turn
		step += 1
		current_player = 'p1'
		board_updated = minimax_decision(search_depth, board_updated, 'p1', True, step)
		print_board(board_updated, step)
		check_win(board_updated)

		# player 2's turn 
		step += 1
		current_player = 'p2'
		if human: # by human
			board_updated = player_2_human(board_updated)
		else: # by computer
			board_updated = minimax_decision(search_depth, board_updated, 'p2', True, step)
		print_board(board_updated, step)
		check_win(board_updated)

		# Other Features

		# 1. Deepen the search when the total number of resources drops to certain thresholds
		if deepen_1:
			if len(positions_all('p1',board_updated)) + len(positions_all('p2',board_updated)) <= 10:  
				search_depth += 1
				deepen_1 = False
		if deepen_2: 
			if len(positions_all('p1',board_updated)) + len(positions_all('p2',board_updated)) <= 5: 
				search_depth += 1
				deepen_2 = False

		# 2. Change the search depth when deadlock appears
		if board_updated in states_cache: 
			search_depth -= 1 if search_depth>4 else -3
		states_cache.pop(0)
		states_cache.append(board_updated)
		
		# 3. Terminate the game if reaching certain threshold 
		if count_minimax >= threshold: 
			print 'Seems not easy to reach the end of the game! Let\'s stop here.'
			break





if __name__ == '__main__':
	main()