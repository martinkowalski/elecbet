classdef Bet < handle
    %BET Single bet on Austrian legislative elections
    %   Detailed explanation goes here
    
    properties
        Bookmaker        
        Odds
        EvalType        
    end
    
    properties (Dependent)
        Description
    end
    
    methods
        function obj = Bet(bookmaker,odds,evalType)
            %BET Ctor
            %   Detailed explanation goes here
            obj.Bookmaker = bookmaker;            
            obj.Odds = odds;
            obj.EvalType = evalType;            
        end
        
        function descr = get.Description(bet)
            %DESCRIPTION of bet
            descr = bet.EvalType.Description;
        end
        
        function [b,p] = iswon(bet,R)
            %ISWON True if bet is won.
            %   b = iswon(bet,R) liefert true für jede Zeile von R zurück
            %   in der die Gewinnbedingungen der bet erfüllt sind.
            %   [b,p] = iswon(bet,R) liefert zusätzlich die
            %   Gewinnwahrscheinlichkeit der bet basierend auf R zurück.
            b = bet.EvalType.iswon(R);
            if nargout > 1, p = sum(b)/size(R,1); end                
        end
        
        function disp(bet)
            %DISP Displays summary of bet
            fprintf('  %s, %s, Quote: %0.2f\n\n', ...
                bet.Bookmaker, bet.Description, bet.Odds)
        end
    end
end

