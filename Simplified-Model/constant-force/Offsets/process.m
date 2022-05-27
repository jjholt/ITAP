clc;clear;
grouped_data = import_csv();
[spigot, collar, stem] = split_data(grouped_data);

offset = (1:2:40)';
spigot_max_displacement = zeros(size(offset));
stem_max_displacement = zeros(size(offset));
collar_max_displacement = zeros(size(offset));

for n = 1:numel(offset)

    stem_magnitude = sqrt(sum(stem{n}(:,2:4).^2, 2));
    stem_max_displacement(n) = max(stem_magnitude);

    spigot_magnitude = sqrt(sum(spigot{n}(:,2:4).^2, 2));
    spigot_max_displacement(n) = max(spigot_magnitude);

    collar_magnitude = sqrt(sum(collar{n}(:,2:4).^2, 2));
    collar_max_displacement(n) = max(collar_magnitude);
end

writetable(table(offset, spigot_max_displacement, stem_max_displacement, collar_max_displacement), "offset_displacements.csv");


p_spigot = polyfit(offset, spigot_max_displacement, 1);
p_collar = polyfit(offset, collar_max_displacement, 1);
p_stem = polyfit(offset, stem_max_displacement, 1);

hold on;
plot(offset, spigot_max_displacement, "DisplayName", "Spigot")
plot(offset, stem_max_displacement, "DisplayName", "Stem")
plot(offset, collar_max_displacement, "DisplayName", "Collar")
legend;

x = (1:200);
y_spig = polyval(p_spigot, x);
y_coll = polyval(p_collar, x);
y_stem = polyval(p_stem, x);

plot(x, y_spig, "LineStyle", "--")
plot(x, y_coll, "LineStyle", "--")
plot(x, y_stem, "LineStyle", "--")
