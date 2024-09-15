classdef BettingSlip < handle
    %BETTINGSLIP Compilation of single bets
    %   BettingSlip erstellt Bets mit dem passenden BetEvaluationType und
    %   legt diese im Array SingleBets ab.
    
    properties
        Stake
    end
    
    properties (SetAccess = immutable)
        AllParties
    end
    
    properties (Dependent)
        NumberOfBets
        Odds
        Wagers
    end
    
    properties (Access = private)
        BetCreator
        SingleBets
        Weights
    end
    
    methods
        function bs = BettingSlip(allParties)
            %BETTINGSLIP Ctor
            bs.Stake = 0;
            bs.AllParties = allParties;
            bs.BetCreator = BetCreator;            
            bs.SingleBets = Bet.empty;            
            bs.Weights = double.empty;
        end
        
        function n = get.NumberOfBets(bs)
            %NUMBEROFBETS Total number of single bets
            n = length(bs.SingleBets);
        end
        
        function q = get.Odds(bs)
            %GETODDS of all SingleBets
            if bs.NumberOfBets > 0
                q = [bs.SingleBets.Odds];
            end
        end
        
        function w = get.Wagers(bs)
            %GETWAGES Return wages based on Stake and Weights
            w = round(bs.Stake * bs.Weights, 2);
        end
        
        function setWeights(bs,w)
            %SETWEIGHTS of all SingleBets
            %   Setzt die Gewichtungen der Einzelwetten. w muss ein Vektor
            %   mit NumberOfBets Elementen sein, jedes Element muss
            %   zwischen 0 und 1 liegen, sum(w) muss 1 sein.
            
            if length(w) ~= bs.NumberOfBets     % check w
                error('Invalid length of w')
            elseif any(w < 0 | w > 1)
                error('Not all elements of w betwen 0 and 1')
            elseif abs(sum(w)-1) > length(w) * eps(class(w))
                error('sum(w) not equal to 1')
            else                                % assign w
                bs.Weights = reshape(w,size(bs.SingleBets));
            end
        end 
        
        function addbet(bs,bookmaker,odds,parties1,op,varargin)
            %ADDBET Create and add single bet
            %   Mögliche Wettarten: op
            %   'ltlim' - Less Than Limit, varargin = lim, r(parties1) < lim
            %   'mtlim' - More Than Limit, varargin = lim, r(parties1) > lim
            %   'lelim' - Less or Equal than Limit, varargin = lim, r(parties1) <= lim
            %   'melim' - More or Equal than Limit, varargin = lim, r(parties1) >= lim
            %   'inopenrng'   - In Open Range, varargin = {lowlim,uprlim}, lowlim < r(parties1) < uprlim
            %   'inclosedrng' - In Closed Range, varargin = {lowlim,uprlim}, lowlim <= r(parties1) <= uprlim
            %   'ltparties' - Less Than Parties, varargin = parties2, r(parties1) < r(parties2)
            %   'mtparties' - Mess Than Parties, varargin = parties2, r(parties1) > r(parties2)
            %   'max' - Max votes, r(parties1) = max(r)
            bet = bs.BetCreator.createBet(bs.AllParties,bookmaker,odds,parties1,op,varargin{:});
            disp(bet)
            bs.SingleBets(end+1) = bet;
            bs.resetWeights;
        end
        
        function removebet(bs,idx)
            %REMOVEBET Remove SingleBets(idx)
            irest = true(size(bs.SingleBets));
            irest(idx) = false;
            bs.SingleBets = bs.SingleBets(irest);
            bs.resetWeights;
        end
        
        function [B,P] = iswon(bs,R)
            %ISWON True if single bets in slip are won
            %   [B,P] = iswon(bs,R) wertet jede der nbets in BettingSlip eingetragenen
            %   Wetten aus. Die Resultatmatrix R hat die Größe (nsim x nparties).
            %   B ist eine (nsim x nbets)-true/false-Matrix. P ist ein (1 x nbets)
            %   Vektor mit den Gewinnwahrscheinlichkeiten jeder Einzelwette.            
            nsim = size(R,1);
            nbets = bs.NumberOfBets;
            B = false(nsim,nbets);            
            for i = 1:nbets
                B(:,i) = bs.SingleBets(i).iswon(R);
            end
            if nargout > 1, P = sum(B) / nsim; end                
        end
        
        function g = yield(bs,R,varargin)
            %YIELD of BettingSlip given results R
            %   g = yield(bs,R) berechnet (nsim x 1) Erträge g
            %   (Nettogewinne/Einsatz) für jede Zeile der
            %   (nsim x nparties)-Resultatmatrix R. Für die Gewichtungen
            %   der SingleBets werden die Werte BettingSlip.Weights
            %   verwendet.
            %   g = yield(bs,R,w) berechnet die Erträge g bei einer
            %   Gewichtung der Einzelwetten mit den übergebenen Werten w.    
            if nargin > 2
                w = varargin{1};
            else
                w = bs.Weights;
            end
            g = bs.iswon(R) * (bs.Odds(:) .* w(:)) - 1;
        end            
        
        function T = summary(bs)
            %SUMMARY of BettingSlip
            %   summary(bs) zeigt eine Zusammenfassung alles registrierten Wetten.
            %   T = summary(bs) liefert die Zusammenfassung als table T.
            sumtable = table((1:bs.NumberOfBets)',...
                {bs.SingleBets.Bookmaker}',...
                {bs.SingleBets.Description}',...
                [bs.SingleBets.Odds]',...
                [bs.Wagers]', ...
                'VariableNames',{'No','Bookmaker','Description','Odds','Wager'});
            if nargout > 0
                T = sumtable;
            else
                disp(sumtable);
            end
        end
    end
    
    methods (Access = private)
        function resetWeights(bs)
            %RESETWEIGHTS of all SingleBets
            %   Setzt die Weights für jede SingleBet auf 1/NumberOfBets.
            if bs.NumberOfBets > 0
                bs.Weights = ones(size(bs.SingleBets)) / bs.NumberOfBets;
            else
                bs.Weights = double.empty;
            end
        end
    end
end

