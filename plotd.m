d = csvread('c:\data.csv');
est = d(2:end,1:2);
cam = d(2:end,3:4);

cam(:,1) = cam(:,1) -50
cam(:,2) = cam(:,2) +75



close
figure
hold on
h1 = plot(est(:,1), est(:,2), 'r-x');
h2 = plot(cam(:,1), cam(:,2), 'b');
pos_errors = sqrt((est(:,1) - cam(:,1)).^2 + (est(:,2) - cam(:,2)).^2);
mean_error = mean(pos_errors);
grid on
legend([h1 h2],'Estimate','True position','Location','SouthWest')
ttl = strcat('Minimum trace scheduling, RMS error=', num2str(mean_error,3), 'mm')
title(ttl);
xlabel('mm')
ylabel('mm')