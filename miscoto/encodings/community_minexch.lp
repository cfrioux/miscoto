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

% what is producible if merging both metabolisms (regardless of transport reactions, just from seeds)
    organism(O) :- draft(O).
    organism(O) :- chosen_bacteria(O).

    htarget(M,O) :- target(M), draft(O).

    target_name(M,N,C,O) :- htarget(M,O), species(M,N,C,O).

% metabolites likely to be exchanged
    %not_external(M,N,C,O) :- species(M,N,C,O), not external(C).
    {exchanged(N,C2,O1,O2) : species(M1,N,C1,O1), species(_,N,C2,O2), escope(M1,N,C1,O1), organism(O1), organism(O2), O1!=O2}.

% selected symbionts
    {chosen_bacteria(B) : bacteria(B)}.
    % chosen_bacteria(B) :- bacteria(B), exchanged(N,B,_).

% producible with exchanges, not independantly
escope(M,N,C,O) :- species(M,N,C,O), seed(M), organism(O).
escope(M,N,C,O) :- species(M,N,C,O), exchanged(N,C,_,O), organism(O).
escope(M,N,C,O) :- species(M,N,C,O), product(M,R,O), reaction(R,O),
            organism(O), escope(M2,N2,C2,O) : reactant(M2,R,O).
escope(M,N,C,O) :- species(M,N,C,O), reactant(M,R,O), reaction(R,O), reversible(R,O),
            organism(O), escope(M2,N2,C2,O) : product(M2,R,O).


% still unproducible targets despite the exchanged_metabolites
unproducible_target(M) :- htarget(M,O), species(M,N,C,O), not escope(M,N,C,O).

% newly producible targets
newly_producible_target(M) :- htarget(M,O), escope(M,_,_,O).

% find final producers in initial or selected community with or without cooperation
% activated reactions
activated_coop_selectedcom(R,O) :- reaction(R,O) ; organism(O); escope(M2,_,_,O) : reactant(M2,R,O).
activated_coop_selectedcom(R,O) :- reaction(R,O) ; organism(O); reversible(R,O); escope(M2,_,_,O) : product(M2,R,O).

% find final producers of targets
target_producer_coop_selectedcom(O,T) :- organism(O), target(T), activated_coop_selectedcom(R,O), product(T,R,O).
target_producer_coop_selectedcom(O,T) :- organism(O), target(T), activated_coop_selectedcom(R,O), reactant(T,R,O), reversible(R,O).

#minimize { 1@3,M : unproducible_target(M) ; 0@3 }.
#minimize { 1@2,B : chosen_bacteria(B) ; 0@2 }.
#minimize { 1@1,N,C,O1,O : exchanged(N,C,O1,O) ; 0@1 }.
#show exchanged/4.

#show unproducible_target/1.
#show chosen_bacteria/1.
#show newly_producible_target/1.
#show target_producer_coop_selectedcom/2.
