classdef BetType < handle
    %BETEVALUATION Abstract class for bet evaluation types.
    
    properties (Abstract)
        Description
    end
    
    methods (Abstract)        
        iswon(betType,R)
    end
end

