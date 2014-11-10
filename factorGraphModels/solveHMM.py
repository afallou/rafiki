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
def viterbi(obs, states, trans_p, emit_p, transitions_per_timestep):
    V = [{}]
    path = {}
 
    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = trans_p.getStartProb(y) * emit_p.getProb(y,obs[0])
        path[y] = [y]
 
    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
 
        for y in states:
            (prob, state) = max((V[t-1][y0] * trans_p.getProb(y0, transitions_per_timestep[t], y) * emit_p.getProb(y,obs[t]), y0) for y0 in states)
            V[t][y] = prob
            newpath[y] = path[state] + [y]
 
        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
        
    print_dptable(V)
    (prob, state) = max((V[n][y], y) for y in states)
    return (prob, path[state])
