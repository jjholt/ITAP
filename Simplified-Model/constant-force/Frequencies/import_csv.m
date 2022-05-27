function grouped_data = import_csv()
%IMPORT_CSV Summary of this function goes here
%   Detailed explanation goes here

    dd = dir("csv/*.csv");
    file_names = {dd.name};
    data = cell(numel(file_names),2);
    data(:,1) = regexprep(file_names, '.csv','');
    
    for i = 1:numel(file_names)
        data{i,2} = readmatrix("csv/" + file_names{i});
    end
    
    grouped_data = {};
    for i = 1:3:size(data,1)
        temp = {};
        for j = 0:2
            fff = data(i+j,:);
            temp{j+1} = fff{2};
        end
        grouped_data{end+1} = temp;
    end
end

