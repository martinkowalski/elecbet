classdef Parties < handle
    %PARTIES Austrian political parties 2019
    
    enumeration
        Oevp    (1, [0, 0, 0])
        Spoe    (2, [205/255, 0, 12/255])
        Fpoe    (3, [0, 94/255, 168/255])
        Gruene  (4, [134/255, 232/255, 37/255])
        Neos    (5, [232/255, 65/255, 139/255])
        Jetzt   (6, [0.5, 0.5, 0.5])
        Rest    (7, [0.5, 0.25, 0.25])
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

