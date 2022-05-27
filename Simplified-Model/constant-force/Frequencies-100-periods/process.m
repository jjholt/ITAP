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

writetable(table(frequency, spigot_max_magnitude, collar_max_magnitude, stem_max_magnitude), "magnitudes.csv")

% Change relative to spigot
T = table(frequency, stem_max_magnitude./spigot_max_magnitude, collar_max_magnitude./spigot_max_magnitude, spigot_max_magnitude./spigot_max_magnitude);
T = renamevars(T, 1:width(T), ["frequency", "stem_relative_magnitude", "collar_relative_magnitude", "spigot_relative_magnitude"]);
writetable(T, "relative_magnitudes.csv")

save("maxima-and-tail", "collar_max_magnitude", "spigot_max_magnitude", "stem_max_magnitude");