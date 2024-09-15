classdef Parties < handle
    %PARTIES Austrian political parties general election 2024
    
    enumeration
        Spoe    (1, [205/255, 0, 12/255])
        Oevp    (2, [0, 0, 0])        
        Gruene  (3, [134/255, 232/255, 37/255])
        Fpoe    (4, [0, 94/255, 168/255])
        Neos    (5, [232/255, 65/255, 139/255])
        Kpoe    (6, [172/255, 18/255, 21/255])
        Bier    (7, [1, 237/255, 0])
        Rest    (8, [0.5, 0.25, 0.25])
    end
    
    properties
        Index
        RGBColor
    end
    
    methods
        function obj = Parties(i,rgb)
            %PARTIES Ctor
            obj.Index = i;
            obj.RGBColor = rgb;
        end
    end 
end

