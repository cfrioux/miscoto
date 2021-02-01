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

% what is producible by host

dscope(M) :- seed(M).

dscope(M) :- draft(D), product(M,R,D), reaction(R,D),
           dscope(M2) : reactant(M2,R,D).

dscope(M) :- draft(D), reactant(M,R,D), reaction(R,D), reversible(R,D),
           dscope(M2) : product(M2,R,D).

% % what is producible by each org

% oscope(M,O) :- seed(M), organism(O).
% oscope(M,O) :- organism(O), product(M,R,O), reaction(R,O),
%            oscope(M2,O) : reactant(M2,R,D).
% oscope(M,O) :- organism(O), reactant(M,R,O), reaction(R,O), reversible(R,O),
%            oscope(M2,O) : product(M2,R,O).


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

% newly producible targets through cooperation
newly_producible_target(M) :- target(M), selescope(M), not dscope(M).

% all producible targets whether individually or collectively
producible_target(M) :- target(M), selescope(M).

% find final producers in initial or selected community with or without cooperation
% activated reactions
% activated_solo_selectedcom(R,O) :- reaction(R,O) ; chosen_org(O); oscope(M2,O) : reactant(M2,R,O).
% activated_solo_selectedcom(R,O) :- reaction(R,O) ; chosen_org(O); reversible(R,O); oscope(M2,O) : product(M2,R,O).

activated_coop_selectedcom(R,O) :- reaction(R,O) ; chosen_org(O); selescope(M2) : reactant(M2,R,O).
activated_coop_selectedcom(R,O) :- reaction(R,O) ; chosen_org(O); reversible(R,O); selescope(M2) : product(M2,R,O).

% find final producers of targets
% target_producer_solo_selectedcom(O,T) :- chosen_org(O), target(T), activated_solo_selectedcom(R,O), product(T,R,O).
target_producer_coop_selectedcom(O,T) :- chosen_org(O), target(T), activated_coop_selectedcom(R,O), product(T,R,O).
target_producer_coop_selectedcom(O,T) :- chosen_org(O), target(T), activated_coop_selectedcom(R,O), reactant(T,R,O), reversible(R,O).

#minimize { 1@1,B : chosen_bacteria(B)}.

#show unproducible_target/1.
#show producible_target/1.
#show chosen_bacteria/1.
#show newly_producible_target/1.
% #show target_producer_solo_selectedcom/2.
#show target_producer_coop_selectedcom/2.
