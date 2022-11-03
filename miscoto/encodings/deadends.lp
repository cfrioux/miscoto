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

product(M,R) :- reaction(R,_), reactant(M,R,_), reversible(R).
reactant(M,R) :- reaction(R,_), product(M,R,_), reversible(R).

deadend_np(M) :- reaction(R,_), reactant(M,R,_), not product(M,R2,_):reaction(R2,_).
deadend_nc(M) :- reaction(R,_), product(M,R,_), not reactant(M,R2,_):reaction(R2,_).

#show deadend_np/1.
#show deadend_nc/1.
