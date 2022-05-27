clc;clear;
grouped_data = import_csv();
nodes = {};
[nodes{1}, nodes{2}, nodes{3}] = split_data(grouped_data);
names = ["base", "collar", "stem"];
t = nodes{1}{1}(:,1);
% frequencies = [1, 10, 20, 30, 40];
% frequencies = [frequencies 50:50:900];
% base_max_magnitude = zeros(size(frequencies));
% stem_max_magnitude = zeros(size(frequencies));
% rms_stem = zeros(size(frequencies));
% rms_base = zeros(size(frequencies));
amplitudes = [1e-2; 5e-3; 1e-3; 2e-4];
% max_magnitude = zeros(size(amplitudes,1),numel(nodes));
for i = 1:numel(nodes)
    max_magnitude = [];
    for n = 1:numel(amplitudes)
        magnitude = sqrt(sum(nodes{i}{n}(:,2:4).^2, 2));
        max_magnitude(n,1) = max(magnitude);
    end
%     max_magnitude = max_magnitude';
    writetable(table(amplitudes, max_magnitude), names(i)+".csv")
end

% 
%     stem_magnitude = sqrt(sum(stem{n}(:,2:4).^2, 2));
%     stem_max_magnitude(n) = max(stem_magnitude);
%     rms_stem(n) = rms(stem_magnitude);
% 
%     base_magnitude = sqrt(sum(base{n}(:,2:4).^2, 2));
%     base_max_magnitude(n) = max(base_magnitude);
%     rms_base(n) = rms(base_magnitude);
% end