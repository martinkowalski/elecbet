classdef SinglePoll < handle
    %SINGLEPOLL Eine einzelne Wahlumfrage
    %   Speichert die Daten einer einzelnen Umfrage. Shares enth�lt immer
    %   die Anteile aller in der Klasse Parties definierten Parteien.
    %   Ist die Summe der �bergebenen shares ~= 1, besteht Shares nur aus
    %   NaN-Eintr�gen.
    
    properties        
        Date
        Institute
        NumberOfRespondents
        Parties
        Shares        
    end
    
    methods
        function poll = SinglePoll(date,institute,numberOfRespondents,parties,shares)
            %SINGLEPOLL Ctor
            
            % Pr�fung �bergebene Parteien
            pidx = [parties.Index];
            validateattributes(sort(pidx),{'numeric'},{'increasing'});
            % Pr�fung �bergebene Anteile            
            validateattributes(shares,{'numeric'},{'>=',0,'<',1},5);            
            % Zuordnung �bergebene parties und shares entsprechend der
            % vorgegebenen Ordnung in Klasse Parties
            if sum(shares) == 1                
                s(pidx) = shares;
                parties(pidx) = parties;                
            else
                s = NaN(1,length(parties));                
            end
            % Konstruktion poll
            poll.Date = date;
            poll.Institute = institute;
            poll.NumberOfRespondents = numberOfRespondents;
            poll.Parties = parties;
            poll.Shares = s;            
        end
        
        function disp(poll)
            %DISP Display summary of poll
            sharepct = poll.Shares * 100;
            fprintf('  %s, %s, %i Befragte:\n', poll.Date, poll.Institute, poll.NumberOfRespondents)            
            for i = 1:length(poll.Parties)
                fprintf('\t%s:\t%5.2f %%\n', poll.Parties(i), sharepct(i))
            end
            fprintf('\n')
        end
    end
end

