classdef Wahlfang < PollEvaluationMethod
    %WAHLFANG Poll evaluation based on wahlfang method
    %   Auswertungsmethodik Wahlfang. Berücksichtigt alle übergebenen
    %   polls. Jede Poll wird zweifach abgewertet:
    %   1. mit einem konstanten Faktor InitialDegredation,
    %   2. nach ihrem Abstand zum ElectionDate
    
    properties
        InitialDegradation = 0.7;
        DegradationPerDay = 4^(-1/30);
        ElectionDate
    end
    
    methods
        function evalMethod = Wahlfang(electionDate)
            %WAHLFANG Ctor
            %   Parameter electionDate: datetime des Wahltermins.
            
            % Zeitliche Abwertung basierend auf days(electionDate-pollDate)
            evalMethod.ElectionDate = electionDate;
        end
        
        function [sest,neff] = evaluate(evalMethod,polls)
            %EVALUATE Estimate combined shares and effective size of given polls
            %   Gemeinsame Auswertung der polls nach der Wahlfang-Methode
            
            nPolls = length(polls);
            nParties = length(polls(1).Shares);
            pollSizes = [polls.NumberOfRespondents];
            pollDates = [polls.Date];
            
            % 1. Effektive Stichprobenumfänge unter Berücksichtigung von initialer
            % und zeitlicher Abwertung.
            % Zeitliche Abwertungsfaktoren jeder Umfrage            
            daysUntilElection = days(evalMethod.ElectionDate - pollDates);
            temporalDegradation = evalMethod.DegradationPerDay .^ daysUntilElection;
            % Effektive Stichprobenumfänge            
            effPollSizes = round(pollSizes .* evalMethod.InitialDegradation .* temporalDegradation);
            neff = sum(effPollSizes);
            
            % 2. Geschätze Stimmanteile
            % Zusammenstellung aller Umfragewerte in Matrix
            allShares = NaN(nPolls,nParties);
            for i = 1:nPolls
                allShares(i,:) = polls(i).Shares;
            end
            % Gewichtung jeder Stichprobe nach ihrem Umfang
            weights = effPollSizes / neff;
            % Average weighted shares
            sest = weights * allShares;
            % TODO Output Analyse
            
            % 3. Ausgabe
            % TODO Ausgabe
        end
    end
end

