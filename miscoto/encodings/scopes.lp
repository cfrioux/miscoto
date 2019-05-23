% what is producible by the host

dscope(M) :- seed(M).

dscope(M) :- draft(D), product(M,R,D), reaction(R,D),
           dscope(M2) : reactant(M2,R,D).

dscope(M) :- draft(D), reactant(M,R,D), reaction(R,D), reversible(R,D),
           dscope(M2) : product(M2,R,D).

% what targets are producible by the host
dproducible(M) :- target(M), dscope(M).
dunproducible(M) :- target(M), not dscope(M).

% what is producible by the whole microbiome (host + symbionts)

organism(O) :- draft(O).
organism(O) :- bacteria(O).

allscope(M) :- seed(M).

allscope(M) :- organism(O), product(M,R,O), reaction(R,O),
           allscope(M2) : reactant(M2,R,O).

allscope(M) :- organism(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
           allscope(M2) : product(M2,R,O).

aproducible(M) :- target(M), allscope(M).
aunproducible(M) :- target(M), not allscope(M).


% get added value of microbiome: what becomes producible with microbiome and is not in dscope

newscope_with_host(M) :- allscope(M), not dscope(M), species(M,_,_,O), draft(O).
newscope_microbiome(M) :- allscope(M), not dscope(M).

newlyproducible(M) :- aproducible(M), not dproducible(M).

#show dscope/1.
#show newscope_with_host/1.
#show newscope_microbiome/1.
#show dunproducible/1.
#show dproducible/1.
#show aunproducible/1.
#show newlyproducible/1.
