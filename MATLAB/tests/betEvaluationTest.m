% test bet evaluations

% Wettarten
% 'ltlim'       - InOpenRange, 0 <= r(idx) < lim
% 'mtlim'       - InOpenRange, lim < r(idx) <= 1
% 'lelim'       - InClosedRange, 0 <= r(idx) <= lim
% 'melim'       - InClosedRange, lim <= r(idx) <= 1
% 'inopenrng'   - InOpenRange, lowlim < r(idx) < uprlim
% 'inclosedrng' - InClosedRange, lowlim <= r(idx) <= uprlim
% 'ltparties'   - LessThanParties, r(idx1) < r(idx2)
% 'mtparties'   - LessThanParties, r(idx2) < r(idx1)
% 'max'         - MaxVotes, r(i) = max

% preconditions
% Create party vars
o = Parties.Oevp;
s = Parties.Spoe;
f = Parties.Fpoe;
g = Parties.Gruene;
n = Parties.Neos;
j = Parties.Jetzt;
r = Parties.Rest;
allParties = [o,s,f,g,n,j,r];

% Test-Wahlergebnisse
R = [0.35 0.25 0.2  0.1 0.05 0.05 0;
     0.1  0.2  0.35 0.1 0.1  0.1  0.05];
assert(all(sum(R,2) == 1),'Anteile des Beispielresultats summieren nicht auf 1')

%% Test LessThanLimit
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'ltlim',0.35);
addbet(bs,'test',2,[s,f],'ltlim',0.55);

C = iswon(bs,R);
E = [0,1;1,0];
assert(all(C(:)==E(:)))

%% Test LessEqualLimit
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'lelim',0.1);
addbet(bs,'test',2,[s,f],'lelim',0.55);
addbet(bs,'test',2,[s,f],'lelim',0.4499999);

C = iswon(bs,R);
E = [0,1,0;1,1,0];
assert(all(C(:)==E(:)))

%% Test MoreThanLimit
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'mtlim',0.1);
addbet(bs,'test',2,[s,f],'mtlim',0.45);

C = iswon(bs,R);
E = [1,0;0,1];
assert(all(C(:)==E(:)))

%% Test MoreEqualLimit
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'melim',0.35);
addbet(bs,'test',2,[s,f],'melim',0.45);
addbet(bs,'test',2,[s,f],'melim',0.55000001);

C = iswon(bs,R);
E = [1,1,0;0,1,0];
assert(all(C(:)==E(:)))

%% Test InOpenRange
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'inopenrng',0.2,0.4);
addbet(bs,'test',2,o,'inopenrng',0.1,0.35);
addbet(bs,'test',2,r,'inopenrng',0.01,1);
addbet(bs,'test',2,r,'inopenrng',0,0.01);

C = iswon(bs,R);
E = [1,0,0,1;0,0,1,0];
assert(all(C(:)==E(:)))

%% Test InClosedRange
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'inclosedrng',0.2,0.4);
addbet(bs,'test',2,o,'inclosedrng',0.1,0.2);
addbet(bs,'test',2,o,'inclosedrng',0.1,0.35);
addbet(bs,'test',2,r,'inclosedrng',0.01,1);
addbet(bs,'test',2,r,'inclosedrng',0,0.01);

C = iswon(bs,R);
E = [1,0,1,0,1;0,1,1,1,0];
assert(all(C(:)==E(:)))

%% Test MaxVotes
bs = BettingSlip(allParties);
addbet(bs,'test',2,o,'max');
addbet(bs,'test',2,g,'max');

C = iswon(bs,R);
E = [1,0;0,0];
assert(all(C(:)==E(:)))

%% Test MoreThanPartiesHandicap
bs = BettingSlip(allParties);
addbet(bs,'test',2,f,'mtphandicap',-0.1,g);
addbet(bs,'test',2,[g,n],'mtphandicap',0.06,f);

C = iswon(bs,R);
E = [0,1;1,0];
assert(all(C(:)==E(:)))