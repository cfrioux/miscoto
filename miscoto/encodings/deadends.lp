% Copyright (C) 2018-2023 Clémence Frioux & Arnaud Belcour - Inria Dyliss - Pleiade
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

% Compute the scope of all the networks when having seeds.
dscope(M) :- seed(M).

dscope(M) :- product(M,R,_), reaction(R,_),
           dscope(M2) : reactant(M2,R,_).

dscope(M) :- reactant(M,R,_), reaction(R,_), reversible(R,_),
           dscope(M2) : product(M2,R,_).

% Compute the reactions that are activated and then can be used to compute deadend/orphan from seeds.
activatedReaction(R) :- reactant(M,R,_), dscope(M2) : reactant(M2,R,_), reaction(R,_).
activatedReaction(R) :- reactant(M,R,_), dscope(M2) : product(M2,R,_); reversible(R,_), reaction(R,_).

% Get all producible metabolites.
activatedProduct(M,R,O) :- activatedReaction(R), reactant(M,R,O), reversible(R,O).
activatedReactant(M,R,O) :- activatedReaction(R), product(M,R,O), reversible(R,O).
activatedReactant(M,R,O) :- activatedReaction(R), reactant(M,R,O).
activatedProduct(M,R,O) :- activatedReaction(R), product(M,R,O).

% Get deadend and orphan metabolites from seeds.
deadend_np(M, seeds) :- activatedReaction(R), activatedReactant(M,R,_), not activatedProduct(M,R2,_):activatedReaction(R2).
deadend_nc(M, seeds) :- activatedReaction(R), activatedProduct(M,R,_), not activatedReactant(M,R2,_):activatedReaction(R2).

% Get all products and reactants.
allProduct(M,R,O) :- reaction(R,O), reactant(M,R,O), reversible(R,O).
allReactant(M,R,O) :- reaction(R,O), product(M,R,O), reversible(R,O).
allReactant(M,R,O) :- reaction(R,O), reactant(M,R,O).
allProduct(M,R,O) :- reaction(R,O), product(M,R,O).

% Compute the deadend/orphan metabolites on all metabolic networks.
deadend_np(M, withoutSeeds) :- reaction(R,_), allReactant(M,R,_), not allProduct(M,R2,_):reaction(R2,_); not dscope(M).
deadend_nc(M, withoutSeeds) :- reaction(R,_), allProduct(M,R,_), not allReactant(M,R2,_):reaction(R2,_); not dscope(M).

#show deadend_np/2.
#show deadend_nc/2.
#show activatedReaction/1.