% what is producible by host

dscope(M) :- seed(M).

dscope(M) :- draft(D), product(M,R,D), reaction(R,D),
           dscope(M2) : reactant(M2,R,D).

dscope(M) :- draft(D), reactant(M,R,D), reaction(R,D), reversible(R,D),
           dscope(M2) : product(M2,R,D).

% dproducible(M) :- target(M), dscope(M).

organism(O) :- draft(O).
organism(O) :- bacteria(O).
% what is producible by host reactions + all bacterial reactions
% We consider one "soup" of metabolism that includes all host + symbionts reactions
% we simply merge the reactions altogether

all_scope(M) :- seed(M).
all_scope(M) :- organism(O), product(M,R,O), reaction(R,O),
           all_scope(M2) : reactant(M2,R,O).
all_scope(M) :- organism(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
           all_scope(M2) : product(M2,R,O).


{chosen_bacteria(B) : bacteria(B)}.

chosen_org(O) :- draft(O).
chosen_org(O) :- chosen_bacteria(O).

selescope(M) :- seed(M).
% selescope(M) :- draft(D), product(M,R,D), reaction(R,D),
%            selescope(M2) : reactant(M2,R,D).
% selescope(M) :- draft(D), reactant(M,R,D), reaction(R,D), reversible(R,D),
%            selescope(M2) : product(M2,R,D).
selescope(M) :- chosen_org(O), product(M,R,O), reaction(R,O),
           selescope(M2) : reactant(M2,R,O).
selescope(M) :- chosen_org(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
           selescope(M2) : product(M2,R,O).

% maximize number of produced targets
:- target(M), all_scope(M), not selescope(M).

% unproducible targets
unproducible_target(M) :- target(M), not all_scope(M).

% newly producible targets
newly_producible_target(M) :- target(M), selescope(M), not dscope(M).


#minimize { 1@1,B : chosen_bacteria(B)}.

#show unproducible_target/1.
#show chosen_bacteria/1.
#show newly_producible_target/1.
