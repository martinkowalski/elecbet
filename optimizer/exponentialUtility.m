function u = exponentialUtility(netGain,p,s)
%EXPONENTIALUTILITY Exponential utility function
%   Exponentielle Nutzenfunktion
%       u(g) = 1 - exp(a * g)
%   mit
%       u(g <= -s) = 0,
%       u(0) = p.
r = netGain > -s;
u = zeros(size(netGain));
u(r) = 1 - (1 - p) .^ (netGain(r)/s + 1);
end

