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
def viterbi(obs, states, trans_p, emit_p, transitions_per_timestep, verbose=False):
    if verbose:
        print "Obs:", obs, "Transitions per timestep", transitions_per_timestep

    if len(obs) == 0 and len(transitions_per_timestep)==0: 
        return (0,[])

    assert(len(obs) == 1 + len(transitions_per_timestep))
    timesteps = len(obs)
    V = [{} for t in range(timesteps)]
    path = {}
 
    # Initialize base cases (t == 0)
    for state in states:
        V[0][state] = trans_p.getStartProb(state) * emit_p.getProb(state,obs[0])
        path[state] = [state]
    # print 'start with a?' + Maybestr(trans_p.transProb['a'])
    print 'initializing V: ' + str(V)
 
    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        newpath = {}

        for state in states:
            for prev_state in states:
                (prob, old_state) = max(
                [(V[t-1][prev_state] 
                    * trans_p.getProb(prev_state, transitions_per_timestep[t - 1], state) 
                    * emit_p.getProb(state,obs[t]), prev_state) for prev_state in states], key=lambda x:x[0])
            # print 'proba======',prob
            V[t][state] = prob
            newpath[state] = path[old_state] + [state]
 
        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t

    if verbose:
        print 'viterbi dp table'
        print(V)

    (prob, state) = max( ((V[n][state], state) for state in states), key=lambda x:x[0])
    return (prob, path[state])
