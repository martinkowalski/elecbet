classdef BetCreator
    %BETCREATOR Factory for Bet creation
    %   Detailed explanation goes here
    
    methods (Static)
        function bet = createBet(allParties,bookmaker,odds,party1,op,varargin)
            %CREATEBET Creates a bet.
            %   Check der allgemeinen Parameter, Anforderung eines
            %   passenden BetEvaluation Objekts und Zusammenstellung der
            %   bet.
            
            % Check argins            
            validateattributes(odds,{'numeric'},{'scalar','>',1},2);
            validateattributes(party1,{'Parties'},{'vector'},3);
            % Valid operators
            validatestring(op,{'ltlim','mtlim','lelim','melim',...
                'inopenrng','inclosedrng','ltparties','mtparties',...
                'max','mtphandicap'},4);
            % varargs are checked in ctor of BetEvaluation object                        
            % Konstruktion Wetttyp/Auswertungsmethodik inkl. Beschreibung
            evalType = BetCreator.createBetEvaluation(allParties,party1,op,varargin{:});            
            % Create Bet
            bet = Bet(bookmaker,odds,evalType);
        end         
    end
    
    methods (Static, Access = private)
        function evalType = createBetEvaluation(allParties,party1,op,varargin)
            %CREATEBETEVAL Factory method for creation of BetEvaluation.
            %   Erstellung einer passenden Strategieklasse zur Auswertung
            %   der Bet.            
            switch op
                case 'ltlim' % => InOpenRange, 0 <= r(idx) < lim
                    lim = varargin{1};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InOpenRange(0,party1,lim);
                    
                case 'mtlim' % => InOpenRange, lim < r(idx) <= 1
                    lim = varargin{1};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InOpenRange(lim,party1,1);
                    
                case 'lelim' % => InClosedRange, 0 <= r(idx) <= lim
                    lim = varargin{1};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InClosedRange(0,party1,lim);
                    
                case 'melim' % => InClosedRange, lim <= r(idx) <= 1
                    lim = varargin{1};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InClosedRange(lim,party1,1);
                    
                case 'inopenrng'    % => InOpenRange, lowlim < r(idx) < uprlim
                    lowlim = varargin{1};
                    uprlim = varargin{2};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InOpenRange(lowlim,party1,uprlim);
                    
                case 'inclosedrng'  % => InClosedRange, lowlim <= r(idx) <= uprlim
                    lowlim = varargin{1};
                    uprlim = varargin{2};
                    BetCreator.checkParties(party1,allParties);
                    evalType = InClosedRange(lowlim,party1,uprlim);
                    
                case 'ltparties' % => LessThanParties, r(idx1) < r(idx2)
                    party2 = varargin{1};
                    BetCreator.checkParties([party1,party2],allParties);
                    evalType = LessThanParties(party1,party2);
                    
                case 'mtparties' % => LessThanParties, r(idx2) < r(idx1)
                    party2 = varargin{1};
                    BetCreator.checkParties([party1,party2],allParties);
                    evalType = LessThanParties(party2,party1);
                    
                case 'max' % => MaxVotes, r(i) = max
                    BetCreator.checkParties(party1,allParties);
                    evalType = MaxVotes(party1);
                    
                case 'mtphandicap' % => MoreThanPartiesHandicap, r(idx1) + handicap > r(idx2)
                    handicap1 = varargin{1};
                    party2 = varargin{2};
                    BetCreator.checkParties([party1,party2],allParties);
                    evalType = MoreThanPartiesHandicap(party1,handicap1,party2);
            end            
        end
        
        function checkParties(givenParties,allParties)
            %CHECKPARTIES Check given parties
            %   checkParties(allParties,givenParties) prüft
            %   1. Ob givenParties Teil der im BettingSlip registrierten
            %   allParties sind,
            %   2. Ob givenParties keine Partei doppelt enthält.
            %   Bricht im Fehlerfall mit entsprechender Fehlermeldung ab.
            
            % Check members
            allmembers = all(ismember(givenParties,allParties));
            if ~allmembers, error('Unknown parties given.'), end
            % Check uniqueness
            givenIdx = sort([givenParties.Index]);
            validateattributes(givenIdx,{'numeric'},{'increasing'});
        end            
    end
end

