classdef InClosedRange < BetType
    %INCLOSEDRANGE Bet type InClosedRange
    %   Auswertungsmethodik iswon(R):
    %       lowlim <= R(:,Party.Index) <= uprlim,
    %   R ist eine m x n Matrix mit gesampelten Wahlausgängen (jede Zeile 
    %   eine simulierte Wahl), idx Partei-Indizes aus {1,...,n},
    %   0 <= lowlimit <= 1, 0 <= uprlimit <= 1 skalare Grenzwerte.    
    
    properties
        Party
        LowerLimit
        UpperLimit
        Description
    end
    
    methods
        function betType = InClosedRange(lowlim,party,uprlim)
            %INCLOSEDRANGE Ctor
            %   Erstellt betType InClosedRange und passende Description
            
            % Check argin
            [idx,isort] = sort([party.Index]);
            % idx must contain unique values
            validateattributes(idx,{'numeric'},{'increasing'});
            validateattributes(lowlim,{'numeric'},{'scalar','>=',0,'<',1});
            validateattributes(uprlim,{'numeric'},{'scalar','>',lowlim,'<=',1});
            % Properties
            betType.Party = party(isort);
            betType.LowerLimit = lowlim;
            betType.UpperLimit = uprlim;
            % Bet type description string
            % Formatierung eine party / mehrere parties
            if length(betType.Party) > 1
                pstr = sprintf('{%s}', strjoin(cellstr(betType.Party),' + '));
            else
                pstr = sprintf('%s', betType.Party);
            end
            % Formatierung Beschreibung
            if betType.LowerLimit == 0
                betType.Description = sprintf('%s <= %0.2f %%', pstr, betType.UpperLimit*100);
            elseif betType.UpperLimit == 1
                betType.Description = sprintf('%s >= %0.2f %%', pstr, betType.LowerLimit*100);
            else
                betType.Description = sprintf('%0.2f %% <= %s <= %0.2f %%', ...
                    betType.LowerLimit*100, pstr, betType.UpperLimit*100);
            end
        end
        
        function b = iswon(betType,R)
            %ISWON True if InClosedRange bet is won.
            %   Rückgabe eines (m x 1)-true-false Vektors b.
            idx = [betType.Party.Index];
            s = sum(R(:,idx),2);
            if betType.LowerLimit > 0
                b = betType.LowerLimit <= s;
                if betType.UpperLimit < 1
                    b = b & s <= betType.UpperLimit;
                end
            else
                b = s <= betType.UpperLimit;
            end
        end
    end
end

