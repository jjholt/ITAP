clc;clear;
flanged = readmatrix("Flanged/magnitudes_flanged.csv");
simplified = readmatrix("Frequencies/magnitudes_simplified.csv");

% figure; hold on;
% a = horzcat(simplified(:,1), abs((flanged(:,2:4) - simplified(:,2:4))./simplified(:,2:4))); 
% ylabel("$\frac{F-S}{S}$", Interpreter="latex")
a = horzcat(simplified(:,1), abs((simplified(:,2:4) - flanged(:,2:4))./flanged(:,2:4))); 
% ylabel("$\frac{F-S}{F}$", Interpreter="latex")

% plot(a(:,1), a(:,4), "DisplayName", "Stem")
% plot(a(:,1), a(:,3), "DisplayName", "Collar")
% plot(a(:,1), a(:,2), "DisplayName", "Spigot")
% legend;

T = array2table(a);
T.Properties.VariableNames(1:4) = {'Frequency','Spigot_error', 'Collar_error', 'Stem_error'};
writetable(T,'error_flanged-simplified.csv')
% writematrix(a, "error_flanged-simplified.csv")