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

% identify who is able to produce the targets (final producers)

% % what is producible by each org
% oscope(M,O) :- seed(M), organism(O).
% oscope(M,O) :- organism(O), product(M,R,O), reaction(R,O),
%            oscope(M2,O) : reactant(M2,R,D).
% oscope(M,O) :- organism(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
%            oscope(M2,O) : product(M2,R,O).

% activated_solo_initcom(R,O) :- reaction(R,O) ; organism(O); oscope(M2,O) : reactant(M2,R,O).
% activated_solo_initcom(R,O) :- reaction(R,O) ; organism(O); reversible(R,O); oscope(M2,O) : product(M2,R,O).

activated_coop_initcom(R,O) :- reaction(R,O) ; organism(O); allscope(M2) : reactant(M2,R,O).
activated_coop_initcom(R,O) :- reaction(R,O) ; organism(O); reversible(R,O); allscope(M2) : product(M2,R,O).

% target_producer_solo_initcom(O,T) :- organism(O), target(T), activated_solo_initcom(R,O), product(T,R,O).

target_producer_coop_initcom(O,T) :- organism(O), target(T), activated_coop_initcom(R,O), product(T,R,O).

target_producer_coop_initcom(O,T) :- organism(O), target(T), activated_coop_initcom(R,O), reactant(T,R,O), reversible(R,O).

#show dscope/1.
#show newscope_with_host/1.
#show newscope_microbiome/1.
#show dunproducible/1.
#show dproducible/1.
#show aunproducible/1.
#show newlyproducible/1.
#show target_producer_coop_initcom/2.
% #show target_producer_solo_initcom/2.
