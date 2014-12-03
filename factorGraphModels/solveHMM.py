import heapq


def viterbi(obs, states, trans_p, emit_p, transitions_per_timestep, verbose=False, numResults=5):
    """
    Gets the highest probability assignment for the HMM.
    Args:
        obs: list of observations
        states: list of states
        trans_p: trans_p[a_0][sep][a_1] gives you the prob of moving from state a_0 to a_1 given separator sep between them
        emit_p: emit_p[obs][state] gives you the prob of emiting obs from state 
    Returns:
        a tuple with the probability of the assignment and the assignment
    """
    if verbose:
        print "Obs:", obs, "Transitions per timestep", transitions_per_timestep
    assert(len(obs) != 0)
    assert(len(obs) == 1 + len(transitions_per_timestep))
    timesteps = len(obs)

    # V is a list of maps, where each map is state => [best prob, second best prob]
    V = [{} for t in range(timesteps)]
    # path is a map from state to [[best way of getting there][second best way of getting there]]
    path = {}
 
    # Initialize base cases (t == 0)
    if not obs[0].isName:
        start_states = [obs[0]]
    else:
        start_states = states

    # initial timestemp 
    for start_state in start_states:
        V[0][start_state] =  [0 for _ in xrange(numResults-1)] + [trans_p.getStartProb(start_state) * emit_p.getProb(start_state,obs[0])]
        path[start_state] = [[start_state] for _ in xrange(numResults)]
    
    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        # print 'path', path
        newpath = {}

        if not obs[t-1].isName:
            prev_states = [obs[t-1]]
        else: 
            prev_states = states

        options = [] 
        if not obs[t].isName:
            for prev_state in prev_states:
                for i in xrange(numResults):
                    prob = V[t-1][prev_state][i] * trans_p.getProb(prev_state, transitions_per_timestep[t - 1], obs[t]) * emit_p.getProb(obs[t],obs[t])
                    options.append((prob, prev_state, i))
            topResults = heapq.nlargest(numResults,options)
            V[t][obs[t]] = [prob for prob, _,_ in topResults] 
            newpath[obs[t]] = [path[old_state][i] + [obs[t]] for _,old_state,i in topResults]
 
        else:
            for state in states: 
                for prev_state in prev_states:  
                    for i in xrange(numResults):    
                        prob = V[t-1][prev_state][i] * trans_p.getProb(prev_state, transitions_per_timestep[t - 1], state) * emit_p.getProb(state,obs[t])
                        options.append((prob, prev_state, i))
                topResults = heapq.nlargest(numResults, options)
                V[t][state] = [prob for prob, _, _ in topResults] 
                newpath[state] = [path[old_state][i] + [state] for _,old_state, i in topResults]
 
        # Don't need to remember the old paths
        path = newpath

    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t

    # if verbose:
    #     print 'viterbi dp table'
    #     print(V)

    if not obs[len(obs)-1].isName:
        end_states = [obs[len(obs)-1]]
    else:
        end_states = states

    # get the top numResults states to end up in 
    end_options = []
    for state in end_states:
        for i in xrange(numResults): 
            end_options.append((V[n][state][i], path[state][i]))

    # (prob, state) = max( ((V[n][state], state) for state in end_states), key=lambda x:x[0])
    return heapq.nlargest(numResults, end_options)


def particle_filtering(obs, states, trans_p, emit_p, transitions_per_timestep, verbose=False, K=5, candidates_count=100):
    """
    Gets the highest probability assignment for the HMM.

    Args:
        obs: list of observations
        states: list of states
        trans_p: trans_p[a_0][sep][a_1] gives you the prob of moving from state a_0 to a_1 given separator sep between them
        emit_p: emit_p[obs][state] gives you the prob of emiting obs from state 
        K: particles we get in the end
        candidates_count: number of candidates we propose at each timestep

    Returns:    
    """
    if len(obs) == 0 and len(transitions_per_timestep)==0: 
        return (0,[])

    assert(len(obs) == 1 + len(transitions_per_timestep))
    timesteps = len(obs)

    # initialize
    paths = []
    candidates = [{} for _ in xrange(K)]
    for k in xrange(K):
        for _ in xrange(candidates_count):
                candidate = util.weightedRandomChoice(trans_p.startProb)
                candidate_weight = emit_p[obs[0]][candidate]
                candidates[k][candidate] = candidate_weight

    for k in xrange(K):
            next_state = util.weightedRandomChoice(candidates[k])
            paths[k].append(next_state)

    # Run for t > 0
    for t in range(1, timesteps):
        candidates = [{} for _ in xrange(K)]
        for k in xrange(K):
            old_state = path[-1]
            # Propose and reweight
            for _ in xrange(candidates_count):
                candidate = util.weightedRandomChoice(trans_p[old_state][transitions_per_timestep[t-1]])
                candidate_weight = emit_p[obs[t]][candidate]
                candidates[k][candidate] = candidate_weight

        # Resample
        for k in xrange(K):
            next_state = util.weightedRandomChoice(candidates[k])
            paths[k].append(next_state)

    return paths

def legacy_viterbi(obs, states, trans_p, emit_p, transitions_per_timestep, verbose=False):
    # if verbose:
    #     print "Obs:", obs, "Transitions per timestep", transitions_per_timestep

    if len(obs) == 0 and len(transitions_per_timestep)==0: 
        return (0,[])

    assert(len(obs) == 1 + len(transitions_per_timestep))
    timesteps = len(obs)
    V = [{} for t in range(timesteps)]
    path = {}
 
    # Initialize base cases (t == 0)
    if not obs[0].isName:
        start_states = [obs[0]]
    else:
        start_states = states
    for start_state in start_states:
        V[0][start_state] = trans_p.getStartProb(start_state) * emit_p.getProb(start_state,obs[0])
        path[start_state] = [start_state]
    # print 'start with a?' + Maybestr(trans_p.transProb['a'])
    # print 'initializing V: ' + str(V)
 
    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        newpath = {}

        if not obs[t-1].isName:
            prev_states = [obs[t-1]]
        else: 
            prev_states = states

        if not obs[t].isName:
            (prob, old_state) = max([(V[t-1][prev_state] 
                * trans_p.getProb(prev_state, transitions_per_timestep[t - 1], obs[t]) 
                * emit_p.getProb(obs[t],obs[t]), prev_state) for prev_state in prev_states], key=lambda x:x[0])
            V[t][obs[t]] = prob
            newpath[obs[t]] = path[old_state] + [obs[t]]
        else:
            for state in states:                
                (prob, old_state) = max(
                [(V[t-1][prev_state] 
                    * trans_p.getProb(prev_state, transitions_per_timestep[t - 1], state) 
                    * emit_p.getProb(state,obs[t]), prev_state) for prev_state in prev_states], key=lambda x:x[0])
                # print 'proba======',prob
                V[t][state] = prob
                newpath[state] = path[old_state] + [state]
 
        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t

    # if verbose:
    #     print 'viterbi dp table'
    #     print(V)

    if not obs[len(obs)-1].isName:
        end_states = [obs[len(obs)-1]]
    else:
        end_states = states

    (prob, state) = max( ((V[n][state], state) for state in end_states), key=lambda x:x[0])
    return (prob, path[state])
