classdef MoreThanPartiesHandicap < BetType
    %MORETHANPARTIESHANDICAP Bet type MoreThanPartiesHandicap
    %   Auswertung BetType MoreThanPartiesHandicap:
    %       R(:,Party1.Index) + Handicap > R(:,Party2,Index)
    
    properties
        Party1
        Handicap1
        Party2
        Description
    end
    
    methods
        function betType = MoreThanPartiesHandicap(party1,handicap1,party2)
            %MORETHANPARTIESHANDICAP Ctor
            
            % Check handicap1
            validateattributes(handicap1,{'numeric'},{'>=',-1,'<=',1},2)            
            % Check if party indices are unique
            [idx1,isort1] = sort([party1.Index]);
            [idx2,isort2] = sort([party2.Index]);
            validateattributes(sort([idx1,idx2]),{'numeric'},{'increasing'});
            % Properties
            betType.Party1 = party1(isort1);
            betType.Handicap1 = handicap1;
            betType.Party2 = party2(isort2);
            % Bet type description string
            % Formatierung eine party1 / mehrere parties1
            if length(betType.Party1) > 1
                p1str = sprintf('{%s}', strjoin(cellstr(betType.Party1),' + '));
            else
                p1str = sprintf('%s', betType.Party1);
            end
            % Formatierung eine party2 / mehrere parties2
            if length(betType.Party2) > 1
                p2str = sprintf('{%s}', strjoin(cellstr(betType.Party2),' + '));
            else
                p2str = sprintf('%s', betType.Party2);
            end
            % Formatierung Beschreibung            
            betType.Description = sprintf('%s%+0.2f %% > %s', p1str, betType.Handicap1*100, p2str);
        end
        
        function b = iswon(betType,R)
            %ISWON True if MoreThanPartiesHandicap bet is won.
            %   Rückgabe eines (m x 1)-true-false Vektors b.
            idx1 = [betType.Party1.Index];
            idx2 = [betType.Party2.Index];
            b = sum(R(:,idx1),2) + betType.Handicap1 > sum(R(:,idx2),2);
        end
    end
end

