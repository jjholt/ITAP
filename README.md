# Layout
Each folder is one task from the planner (`plan.planner`) and is a milestone in reaching the final model. 

# Finding data
Data is separated into 1) constant force, which are the original simulations where a 0.2 mN force is applied; and 2) constant displacement, where the exact movement is prescribed to the spigot.
 
## Folders and files
1. `Amplitudes`: Varying input amplitudes. Output is maximum displacement magnitude (amplitude).
2. `Error`: The difference between the final and the current interval's amplitude. 
3. `Flanged`: Frequency dependent maximum displacement magnitude (amplitude) for the basic model **with** a flange.
4. `Frequencies`: Frequency dependent maximum displacement magnitude (amplitude) for the model **without** a flange.
5. `Offsets`: Varying position where load is applied on the spigot. Begins at 1 mm from the base and moves up.
6. `error_flanged-simplified.csv`: Relative difference (error) between the extremely simplified model and the one with a flange.

## Raw data
Inside each folder there is a `.csv` file which contains all the raw data.
Raw data is divided by *job* (independent variable) and *node* (part where the sensor was placed).

In matlab you can quickly import all the data in the `.csv` files:
```matlab
grouped_data = import_csv();
[spigot, collar, stem] = split_data(grouped_data);

function grouped_data = import_csv()
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

function [base,collar,stem] = split_data(data)
    for n = 1:numel(data)
        datum = data{n}; % One unit of frequency
        base{n} = datum{1};
        collar{n} = datum{2};
        stem{n} = datum{3};
    end
end
```
