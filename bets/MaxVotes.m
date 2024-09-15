classdef MaxVotes < BetType
    %LESSTHAN Bet type LessThan
    %   Die Auswertungsmethodik MaxVotes repräsentiert die Auswertung von
    %   NRW-Wetten auf die Partei i mit den meisten Stimmen,
    %       R(m,i) = max(R(m,:)).
    %
    %   R ist eine m x n Matrix. Jede Zeile repräsentiert einen Wahlausgang
    %   mit n Parteien. i ist der Index der Partei, die die meisten Stimmen
    %   erhalten haben soll.
    
    properties
        Party
        Description
    end
    
    methods
        function betType = MaxVotes(party)
            %MAXVOTES Ctor
            validateattributes(party,{'Parties'},{'scalar'});
            betType.Party = party;            
            betType.Description = sprintf('meiste Stimmen %s', betType.Party);
        end
        
        function b = iswon(betType,R)
            %ISWON True if bet is won.
            %   Rückgabe eines (m x 1)-true-false Vektors b.
            idx = betType.Party.Index;
            b = R(:,idx) == max(R,[],2);
        end
    end
end

