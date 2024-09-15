classdef Koala < PollEvaluationMethod
    %KOALA Poll evaluation based on wahlfang method
    %   Auswertungsmethodik Koala. Berücksichtigt alle übergebenen
    %   polls. Anteile werden gewichtet gemittelt. Die jede Poll wird
    %   zweifach abgewertet:
    %   1. Nach ihrem Abstand zum Election Date
    %   2. Beim pooling der Umfragen unter Annhame eine Korrelation
    %   SinglePollKorrelation zwischen den Einzelumfragen.

    
    properties
        DegradationPerDay = 4^(-1/30);
        SinglePollCorrelation = 0.5;
        ElectionDate
    end
    
    methods
        function evalMethod = Koala(electionDate)
            %KOALA Ctor
            %   Parameter electionDate: datetime des Wahltermins.
            
            % Zeitliche Abwertung basierend auf days(electionDate-pollDate)
            evalMethod.ElectionDate = electionDate;
        end
        
        function [sest,neff] = evaluate(evalMethod,polls)
            %EVALUATE Estimate combined shares and effective size of given polls
            %   Gemeinsame Auswertung der polls nach der Koala-Methode
            
            nPolls = length(polls);
            nParties = length(polls(1).Shares);
            pollSizes = [polls.NumberOfRespondents];
            pollDates = [polls.Date];            
            
            % 1. Zeitliche Abwertung der Stichprobenumfänge
            % Gemeinsamer Abwertungsfaktor aller Umfragen basierend auf dem
            % mittlerem Umfragedatum
            meanPollDate = mean(pollDates);
            daysUntilElection = days(evalMethod.ElectionDate - meanPollDate);
            temporalDegradation = evalMethod.DegradationPerDay ^ daysUntilElection;
            % Effektive Stichprobenumfänge            
            effPollSizes = round(pollSizes .* temporalDegradation);
            
            % 2. Berechnung des efffektiven Stichprobenumfangs der gepoolten Umfrage
            % Zusammenstellung aller Umfragewerte in Matrix
            allShares = NaN(nPolls,nParties);
            for i = 1:nPolls
                allShares(i,:) = polls(i).Shares;
            end
            % Gewichtung jeder Stichprobe nach ihrem Umfang
            weights = effPollSizes / sum(effPollSizes);
            % Average weighted shares
            sest = weights * allShares;
            
            % 3. Berechnung des effektiven Stichprobenumfangs der
            % gepoolten Umfrage
            % Der effektive Stichprobenumfang wird anhand der bereits
            % zeitlich abgewerteten Einzelumfängen und dem Anteil der
            % ersten (i.d.R. stärksten) Partei berechnet.
            firstShares = allShares(:,1)';
            neff = evalMethod.effectiveSampleSize(effPollSizes,firstShares);            
        end
    end
    
    methods (Access = private)
        function neff = effectiveSampleSize(evalMethod,size,share)
            %EFFECTIVESAMPLESIZE Calculation of the effective size of a pooled poll
            %   Berechnet den effektiven Stichprobenumfang einer gepoolten
            %   Stichprobe basierend auf den in Vektoren zusammengefassten
            %   Umfängen size und den Anteilen share. Die Anteile share sind
            %   die Umfragewerte einer einzelnen Partei in den einzelnen
            %   Umfragen.
            %   Funktionscode übernommen aus KOALA Package.
            weights = size;
            corr = evalMethod.SinglePollCorrelation;
            
            pTotal = sum(weights .* share) / sum(weights);
            varInd = pTotal*(1-pTotal);
            nInst = length(size);
            % nTotal = sum(size);
            varVec = share .* (1 - share) ./ size;
            sdVec = sqrt(varVec);
            nComb = 0;
            for i = (nInst-1):-1:1
                nComb = nComb + i;
            end
            covVec = NaN(1,nComb);
            nCovVec = covVec;
            
            k = nInst - 1;
            count = 1;
            while k > 0
                covVec(count:count+k-1) = corr .* sdVec(1:k) .* sdVec(nInst-k+1:nInst);
                nCovVec(count:count+k-1) = weights(1:k) .* weights(nInst-k+1:nInst);
                count = count + k;
                k = k - 1;
            end
            
            varEst = 1 ./ (sum(weights)).^2 .* (sum((weights.^2) .* varVec) + sum(2 .* nCovVec .* covVec));
            neff = round(varInd / varEst);
        end        
    end
end

