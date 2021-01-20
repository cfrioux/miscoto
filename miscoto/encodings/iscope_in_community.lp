% the scope (seeds nd what they can activate in the MN) of the species of interest

iscope(M,D) :- seed(M), target_species(D).

iscope(M,D) :- target_species(D), product(M,R,D), reaction(R,D),
           iscope(M2,D) : reactant(M2,R,D).

iscope(M,D) :- target_species(D), reactant(M,R,D), reaction(R,D), reversible(R,D),
           iscope(M2,D) : product(M2,R,D).


% its activated reactions
iactiv(R,D) :- target_species(D), reaction(R,D),
            iscope(M2,D) : reactant(M2,R,D).
iactiv(R,D) :- target_species(D), reaction(R,D), reversible(R,D),
            iscope(M2,D) : product(M2,R,D).

% what the target species can actually produce by itself in the seeds

iproduced(M,D) :- product(M, R, D), iactiv(R,D).
iproduced(M,D) :- reactant(M, R, D), iactiv(R,D), reversible(R,D).

% being in a community changes the environment

% determining the scope of the whole community

allscope(M) :- seed(M).

allscope(M) :- bacteria(O), product(M,R,O), reaction(R,O),
           allscope(M2) : reactant(M2,R,O).

allscope(M) :- bacteria(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
           allscope(M2) : product(M2,R,O).

% what can this extended scope activate in the targeted species
% community-activated reactions
cactiv(R,D) :- target_species(D), reaction(R,D),
            allscope(M2) : reactant(M2,R,D).
cactiv(R,D) :- target_species(D), reaction(R,D), reversible(R,D),
            allscope(M2) : product(M2,R,D).

% what the target species can actually produce by itself in the community
cproduced(M,D) :- product(M, R, D), cactiv(R,D).
cproduced(M,D) :- reactant(M, R, D), cactiv(R,D), reversible(R,D).



#show iproduced/2.
#show cproduced/2.
