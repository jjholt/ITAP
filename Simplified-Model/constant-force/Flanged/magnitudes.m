clc;clear;
grouped_data = import_csv();
[spigot, collar, stem] = split_data(grouped_data);

frequency = [1, 10, 20, 30, 40];
frequency = [frequency 50:50:900];
spigot_max_magnitude = zeros(size(frequency));
stem_max_magnitude = zeros(size(frequency));
collar_max_magnitude = zeros(size(frequency));

for n = 1:numel(frequency)
    stem_magnitude = sqrt(sum(stem{n}(:,2:4).^2, 2));
    stem_max_magnitude(n) = max(stem_magnitude);

    collar_magnitude = sqrt(sum(collar{n}(:,2:4).^2, 2));
    collar_max_magnitude(n) = max(collar_magnitude);

    spigot_magnitude = sqrt(sum(spigot{n}(:,2:4).^2, 2));
    spigot_max_magnitude(n) = max(spigot_magnitude);

    
end
frequency = frequency';
spigot_max_magnitude = spigot_max_magnitude';
collar_max_magnitude = collar_max_magnitude';
stem_max_magnitude = stem_max_magnitude';

y = table(frequency, spigot_max_magnitude, collar_max_magnitude, stem_max_magnitude);
writetable(y, "magnitudes_flanged.csv")