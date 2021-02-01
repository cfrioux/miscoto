% Copyright (C) 2018-2021 Clémence Frioux & Arnaud Belcour - Inria Dyliss - Pleiade
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU Lesser General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.

% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
% GNU Lesser General Public License for more details.

% You should have received a copy of the GNU Lesser General Public License
% along with this program. If not, see <http://www.gnu.org/licenses/>

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
