%% Test optimization of interwetten 24.09.2019

electionDate = datetime('29-Sep-2019');

o = Parties.Oevp;
s = Parties.Spoe;
f = Parties.Fpoe;
g = Parties.Gruene;
n = Parties.Neos;
j = Parties.Jetzt;
r = Parties.Rest;

allParties = [o s f g n j r];

%% Wahlumfragen 24.09.2019, Auswertungsmethode Koala
polls = Polls(allParties, Koala(electionDate));

% 12.09., Karmasin, Telefon und Online, 3000 abgewertet auf 1000 Befragte
addpoll(polls,datetime('12-Sep-2019'), 'Karmasin', 1000, [o s f g n j], [0.35 0.22 0.19 0.12 0.09 0.02]); % Rest 0.01

% 14.09., OGM, Telefon und Online, 2167 abgewertet auf 1000 Befragte
addpoll(polls,datetime('14-Sep-2019'), 'OGM', 1000, [o s f g n j], [0.35 0.22 0.20 0.11 0.08 0.02]); % Rest 0.02

% 14.09., Unique Research, Telefon und Online, 2402 abgewertet auf 1000 Befragte
addpoll(polls,datetime('14-Sep-2019'), 'UniqueResearch', 1000, [o s f g n j], [0.33 0.22 0.20 0.13 0.08 0.02]); % Rest 0.02

% 22.09., Unique Research, Telefon und Online, 3021 abgewertet auf 1000 Befragte
addpoll(polls,datetime('22-Sep-2019'), 'Hajek', 1000, [o s f g n j], [0.34 0.22 0.20 0.13 0.08 0.02]); % Rest 0.01

summary(polls)

%% Geschätzte Anteile
[shares,neff] = evaluate(polls)

%% Wetten
bs = BettingSlip(allParties);

addbet(bs,'interwetten',1.85,o,'mtlim',0.345);
addbet(bs,'interwetten',1.85,o,'ltlim',0.345);

addbet(bs,'interwetten',1.85,s,'mtlim',0.225);
addbet(bs,'interwetten',1.85,s,'ltlim',0.225);

addbet(bs,'interwetten',1.85,f,'mtlim',0.205);
addbet(bs,'interwetten',1.85,f,'ltlim',0.205);

addbet(bs,'interwetten',1.85,n,'mtlim',0.08);
addbet(bs,'interwetten',1.85,n,'ltlim',0.08);

addbet(bs,'interwetten',1.95,g,'mtlim',0.125);
addbet(bs,'interwetten',1.75,g,'ltlim',0.125);

addbet(bs,'interwetten',1.90,j,'mtlim',0.02);
addbet(bs,'interwetten',1.80,j,'ltlim',0.02);

T = summary(bs)

bs.Stake = 100; % Wetteinsatz!

%% Optimierung - Gesampelte Wahlausgänge
nsim = 10000;
R = polls.dirsample(nsim);

%% Optimierung - fmincon Parameter 
% Nutzenfunktion
utilityFcn = @(netGain) exponentialUtility(netGain,0.7,bs.Stake);
% Kostenfunktion: Geschätzter Erwartungswert der Nutzenfunktion
fun = @(w) -mean(utilityFcn(bs.Stake * yield(bs,R,w)));
% Beschränkungen
w0 = ones(1,bs.NumberOfBets)/bs.NumberOfBets;
aeq = ones(1,bs.NumberOfBets);
beq = 1;
lb = zeros(bs.NumberOfBets,1);
ub = ones(bs.NumberOfBets,1);
options = optimoptions('fmincon','Display','iter');

%% Optimierung - fmincon
wopt = fmincon(fun,w0,[],[],aeq,beq,lb,ub,[],options)
setWeights(bs,wopt);

%% Ergebnisse - BetSlip summary table
[~,pwin] = iswon(bs,R);
T = addvars(T,pwin(:),'NewVariableNames',{'Pwin'})

%% Ergebnisse - yield Histogramm
netGain = bs.Stake * yield(bs,R);
histogram(netGain,'Normalization','probability')