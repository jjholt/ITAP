clc;clear;
grouped_data = import_csv();
[spigot, collar, stem] = split_data(grouped_data);

frequency = [1; 10; 20; 30; 40];
frequency = [frequency; (50:50:900)'];
spigot_max_magnitude = zeros(size(frequency));
stem_max_magnitude = zeros(size(frequency));
collar_max_magnitude = zeros(size(frequency));
for n = 1:numel(frequency)
    stem_magnitude = sqrt(sum(stem{n}(:,2:4).^2, 2));
    stem_max_magnitude(n,1) = max(stem_magnitude);

    spigot_magnitude = sqrt(sum(spigot{n}(:,2:4).^2, 2));
    spigot_max_magnitude(n,1) = max(spigot_magnitude);

    collar_magnitude = sqrt(sum(collar{n}(:,2:4).^2, 2));
    collar_max_magnitude(n,1) = max(collar_magnitude);
end

writetable(table(frequency, spigot_max_magnitude, collar_max_magnitude, stem_max_magnitude), "magnitudes_simplified.csv")

writetable(table(frequency, spigot_max_magnitude), "spigot_maxima.csv");
writetable(table(frequency, stem_max_magnitude), "stem_maxima.csv");
writetable(table(frequency, collar_max_magnitude), "collar_maxima.csv");

% Change relative to spigot

writetable(table(frequency, (stem_max_magnitude./spigot_max_magnitude), 'VariableNames', {'frequency', 'relative_magnitude'}), "stem_maxima_normalised.csv");
writetable(table(frequency, (collar_max_magnitude./spigot_max_magnitude), 'VariableNames', {'frequency', 'relative_magnitude'}),"collar_maxima_normalised.csv");
writetable(table(frequency, (spigot_max_magnitude./spigot_max_magnitude), 'VariableNames', {'frequency', 'relative_magnitude'}), "spigot_maxima_normalised.csv");

save("maxima-and-tail", "collar_max_magnitude", "spigot_max_magnitude", "stem_max_magnitude");