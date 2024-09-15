%% Test interwetten, MoreThanPartiesHandicap-Wetten, 26.09.2019

electionDate = datetime('29-Sep-2019');

o = Parties.Oevp;
s = Parties.Spoe;
f = Parties.Fpoe;
g = Parties.Gruene;
n = Parties.Neos;
j = Parties.Jetzt;

%% Wahlumfragen
load('polls26092019.mat')
summary(polls);

%% Handicapwetten
bs = BettingSlip;

addbet(bs,'interwetten',1.85,o,'mtphandicap',-0.125,s)
addbet(bs,'interwetten',1.85,s,'mtphandicap',0.125,o)

addbet(bs,'interwetten',1.85,o,'mtphandicap',-0.14,f)
addbet(bs,'interwetten',1.85,f,'mtphandicap',0.14,o)

addbet(bs,'interwetten',1.85,o,'mtphandicap',-0.22,g)
addbet(bs,'interwetten',1.85,g,'mtphandicap',0.22,o)

addbet(bs,'interwetten',1.75,o,'mtphandicap',-0.255,n)
addbet(bs,'interwetten',1.85,n,'mtphandicap',0.255,o)

addbet(bs,'interwetten',1.90,s,'mtphandicap',-0.095,g)
addbet(bs,'interwetten',1.80,g,'mtphandicap',0.095,s)

addbet(bs,'interwetten',1.90,s,'mtphandicap',-0.14,n)
addbet(bs,'interwetten',1.80,n,'mtphandicap',0.14,s)

addbet(bs,'interwetten',1.95,s,'mtphandicap',-0.03,f)
addbet(bs,'interwetten',1.75,f,'mtphandicap',0.03,s)

addbet(bs,'interwetten',1.80,f,'mtphandicap',-0.08,g)
addbet(bs,'interwetten',1.90,g,'mtphandicap',0.08,f)

addbet(bs,'interwetten',1.85,f,'mtphandicap',-0.12,n)
addbet(bs,'interwetten',1.85,n,'mtphandicap',0.12,f)

addbet(bs,'interwetten',1.85,g,'mtphandicap',-0.045,n)
addbet(bs,'interwetten',1.85,n,'mtphandicap',0.045,g)