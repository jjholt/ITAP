clc;clear;
low = load("Frequencies/maxima-and-tail.mat");
high = load("Frequencies-500-periods/maxima-and-tail.mat");

err_collar = zeros(size(high.stem_max_magnitude));
err_spigot = zeros(size(high.stem_max_magnitude));
err_stem = zeros(size(high.stem_max_magnitude));

for i = 1:length(high.tail_end)
    err_collar(:, i) = high.collar_max_magnitude(:,end)./high.collar_max_magnitude(:,i);
    err_spigot(:, i) = high.spigot_max_magnitude(:,end)./high.spigot_max_magnitude(:,i);
    err_stem(:, i)   = high.stem_max_magnitude(:,end)./high.stem_max_magnitude(:,i);
end

vars = 1:numel(high.frequencies) + 1;
names = append("frequency-", string(high.frequencies), "Hz");

a = array2table([high.tail_end' (err_collar - err_collar(:,end))']);
a = renamevars(a, vars, ['time-percent'; names]);
writetable(a, "Error/collar.csv");

b = array2table([high.tail_end' (err_spigot - err_spigot(:,end))']);
b = renamevars(b, vars, ['time-percent'; names]);
writetable(b, "Error/spigot.csv");

c = array2table([high.tail_end' (err_stem - err_stem(:,end))']);
c = renamevars(c, vars, ['time-percent'; names]);
writetable(c, "Error/stem.csv")