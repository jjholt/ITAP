function [base,collar,stem] = split_data(data)
%SPLIT_DATA Summary of this function goes here
%   Detailed explanation goes here
    for n = 1:numel(data)
        datum = data{n}; % One unit of frequency
        base{n} = datum{1};
        collar{n} = datum{2};
        stem{n} = datum{3};
    end
end

