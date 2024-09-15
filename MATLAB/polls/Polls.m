classdef Polls < handle
    %POLLS Collection and evaluation of election polls
    %   Speichert einzelne Wahlumfragen und übergibt sie zur Auswertung an
    %   eine festgelegte EvaluationMethod (Wahlfang oder Koala).
    %   Schätzt die Anteile aller Parteien und einen zugehörigen effentiven
    %   Stichprobenumfang basierend auf einer Kombination aller
    %   Einzelumfragen.
    
    properties (SetAccess = immutable)
        AllParties
    end
    
    properties (Dependent)
        NumberOfPolls
    end
    
     properties (Access = private)
        SinglePolls = SinglePoll.empty;
        EvaluationMethod
        Rounding
    end
    
    methods
        function polls = Polls(allParties,evalMethod)
            %ELECTIONPOLLS Ctor
            polls.AllParties = allParties;           
            %   Auswertungsmethodik evalMethod: Wahlfang oder Koala.
            polls.EvaluationMethod = evalMethod;
            % Angegebene Umfrageergebnisse sind i.d.R. auf 1 % gerundet
            % => maximale Abweichung um Rounding = +/- 0.5 %.
            polls.Rounding = 0.5/100;
        end
        
        function n = get.NumberOfPolls(polls)
            %NUMBEROFPOLLS Total number of entered polls
            n = length(polls.SinglePolls);
        end
        
        function addpoll(polls,date,institute,numberOfRespondents,parties,shares)
            %ADDPOLL Add single Poll
            %   Fügt eine neue Poll hinzu. shares enthält die Anteile der Parteien
            %   parties. Falls Parties.Rest nicht enthalten ist, muss
            %   sum(shares) <= 1 sein und Rest wird automatisch ergänzt. Falls
            %   Rest enthalten ist muss sum(shares) = 1 sein. Ansonsten werden
            %   alle shares als NaN eingetragen.
            
            % Falls die übergebenen parties Parties.Rest (Party mit dem
            % letzten Index) nicht enthalten, wird diese zu parties hinzugefügt
            % und shares so ergänzt, dass sum(shares) == 1
            rest = polls.AllParties(end);
            if ~ismember(parties,rest)
                srest = abs(1-sum(shares));
                p = [parties, rest];
                s = [shares, srest];
            else
                p = parties;
                s = shares;
            end
            % Erstelle poll mit allen Parteien und ergänzten Anteilen
            newPoll = SinglePoll(date,institute,numberOfRespondents,p,s);
            % Füge poll chronologisch in SinglePolls ein: SinglePolls(1): älteste,
            % SinglePolls(end): neueste Umfrage            
            if ~isempty(polls.SinglePolls)
                previousPolls = polls.SinglePolls;
                later = [previousPolls.Date] > newPoll.Date;
                polls.SinglePolls = [previousPolls(~later), newPoll, previousPolls(later)];
            else
                polls.SinglePolls = newPoll;
            end
            disp(newPoll);
        end
        
        function removepoll(polls,idx)
            %REMOVEPOLL Remove Poll(idx)
            irest = true(size(polls.SinglePolls));
            irest(idx) = false;
            polls.SinglePolls = polls.SinglePolls(irest);
        end
        
        function T = summary(polls)
            %SUMMARY of polls
            %   summary(polls) zeigt eine Zusammenfassung aller registrierten Umfragen.
            %   T = summary(polls) liefert die Zusammenfassung als table T.            
            pnames = cellstr(polls.AllParties);
            % Erstellung eines table mit den einzelnen Anteilen jeder Umfrage
            sharray = NaN(polls.NumberOfPolls,length(pnames));
            for i = 1:polls.NumberOfPolls
                sharray(i,:) = polls.SinglePolls(i).Shares;
            end
            % Erstellung eines summary table
            sumtable = table((1:polls.NumberOfPolls)',...
                [polls.SinglePolls.Date]',...
                {polls.SinglePolls.Institute}',...
                sharray,...
                [polls.SinglePolls.NumberOfRespondents]',...
                'VariableNames',{'No','Date','Institute','Shares','n'});
            % Aufteilung der shares in shares der einzelnen Parteien
            sumtable = splitvars(sumtable,'Shares','NewVariableNames',pnames);
            if nargout > 0
                T = sumtable;
            else
                disp(sumtable);
            end
        end
        
        function [sest,neff] = evaluate(polls)
            %EVALUATE set of all given polls
            %   Übergibt alle eingetragenen SinglePolls an den EvaluationMethod. Liefert
            %   die geschätzten Anteile sest und die zugehörige effektive
            %   Umfragegröße neff zurück.
            [sest,neff] = polls.EvaluationMethod.evaluate(polls.SinglePolls);
        end       
        
        function S = mnsample(polls,nsim)
            %MNSAMPLE Create sample of election results
            %   Erstellt ein sample von Wahlausgängen, basierend auf
            %   Multinomialverteilungen MN(shares+/-rounding,neff) vom
            %   Umfang nsim. Die Variation der shares um +/- rounding,
            %   rounding = 0.005 entsprechend 0.5 % soll die Rundung der
            %   verfügbaren Umfrageergebnisse ausgleichen.
            
            % Geschätzte Stimmanteile und effektive Stichprobengröße
            [estimatedShares,neff] = evaluate(polls);
            % Parameter P der Multinomialverteilung durch Variation der estimatedShares
            P = polls.sampleShares(estimatedShares,nsim);
            % Sample von Wahlergebnissen
            S = mnrnd(neff,P)/neff;
        end
        
        function S = dirsample(polls,nsim)
            %DIRSAMPLE Create sample of election results
            %   Erstellt ein sample von Wahlausgängen, basierend auf
            %   Dirichletverteilungen D(alpha) nach der Koala-Methode vom
            %   Umfang nsim. Zur Berechnung von alpha werden die shares um
            %   +/- rounding, rounding = 0.5 entsprechend 0.5 % variert, um
            %   die Rundung der verfügbaren Umfrageergebnisse
            %   auszugleichen.         
            
            % Geschätzte Stimmanteile und effektive Stichprobengröße
            [estimatedShares,neff] = evaluate(polls);
            % Variation der estimatedShares
            P = polls.sampleShares(estimatedShares,nsim);            
            % Berechnung der Parameter der posteriori Dirichlet-Verteilung
            ALPHA = P * neff + 0.5;
            % Sample von Wahlergebnissen
            S = polls.dirrnd(ALPHA);            
        end
        
        function plotSample(polls,R)
            %PLOTSAMPLE Plot histogram of given sample
            %   Plottet ein Histogramm der Stimmanteile in jeder Spalte des
            %   übergebenen Samples R (ausgenommen Rest in der letzten
            %   Spalte).
            pnames = cellstr(polls.AllParties);            
            histogram(R(:,polls.AllParties(1).Index),...
                'FaceColor',polls.AllParties(1).RGBColor,'Normalization','pdf','BinWidth',0.005)
            hold on
            for i = 2:length(pnames)-1 % Letzte Spalte 'Rest' wird nicht geplottet
                histogram(R(:,polls.AllParties(i).Index),...
                'FaceColor',polls.AllParties(i).RGBColor,'Normalization','pdf','BinWidth',0.005)
            end
            hold off
            xlabel('%')
            ylabel('PDF')
            legend(pnames(1:end-1))
            grid
        end
    end
    
    methods (Access = private)
        function S = sampleShares(polls,shares,nsim)
            %SAMPLESHARES Kompensation von Rundungsfehlern der Umfrageergebnisse
            %   Überlagerung der shares mit gleichverteilten Zufallszahlen
            %   im Bereich +/- rounding.
            
            % Check argin
            validateattributes(shares,{'numeric'},{'>=',0,'<=',1},1);
            % Bereichsgrenzen a, b der Gleichverteilung, so dass jeder überlagerte share
            % nicht unter 0 oder über 1 liegen kann.
            a = max(shares - polls.Rounding, 0);
            b = min(shares + polls.Rounding, 1);
            % Sample shares vom Umfang nsim
            nparties = length(shares);
            S = zeros(nsim,nparties);
            for i = 1:nparties
                S(:,i) = unifrnd(a(i),b(i),nsim,1);
            end
            % Normierung des samples
            S = S./sum(S,2);            
        end
        
        function R = dirrnd(~,ALPHA)
            %DIRRND Dirichlet distributed random numbers
            %   Detailed explanation goes here
            aOK = all(ALPHA>0,2);
            R = NaN(size(ALPHA));
            G = gamrnd(ALPHA(aOK,:),1);
            R(aOK,:) = G./sum(G,2);
        end
    end
end

