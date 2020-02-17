% Plot bar graph
clear; clc; close all
% X = categorical({'Raw Data','Feature Data'});
% X = reordercats(X,{'Raw Data','Feature Data'});
X = categorical({'GaussianNB', 'Random Forest', 'KNN (k = 7)', 'Gradient Boost', 'SVM', 'LSTM', 'CNN', 'CNN-LSTM'});
X = reordercats(X,{'GaussianNB', 'Random Forest', 'KNN (k = 7)', 'Gradient Boost', 'SVM', 'LSTM', 'CNN', 'CNN-LSTM'});
Y = [72.480   84.662   61.893   87.207   76.960   89.684   90.458   90.536;
    77.027   92.467   90.329   93.926   94.028   94.829   94.679   94.927
    ];

figure;
b = bar(X,Y);
% legend('GaussianNB', 'Random Forest', 'KNN (k = 7)', 'Gradient Boost', 'SVM', 'LSTM', 'CNN', 'CNN-LSTM')
legend('Raw Data', 'Feature Data')
ylim([60 100])
% b(3).FaceColor = [.2 .6 .5];
xtips1 = b(1).XEndPoints;
ytips1 = b(1).YEndPoints;
labels1 = string(b(1).YData);
text(xtips1,ytips1,labels1,'HorizontalAlignment','center',...
    'VerticalAlignment','bottom')

xtips2 = b(2).XEndPoints;
ytips2 = b(2).YEndPoints;
labels2 = string(b(2).YData);
text(xtips2,ytips2,labels2,'HorizontalAlignment','center',...
    'VerticalAlignment','bottom')

% Acc: 1st row: UCI Raw
%      2nd row: UCI feature
%      3rd row: LAB Raw
%      3rd row: LAB feature (Haar)
% Column: CNN, LSTM, CNN-LSTM, SVM, KNN, GNB
Acc = [90.458 89.684 90.536 76.69 61.893 72.107;
    94.829 94.679 94.927 94.028 93.926 72.48;
    90.525 89.041 94.429 73.288 90.129 93.604;
    90.205 91.66 90.71 66.438 87.443 93.607]
X1 = categorical({'LSTM', 'CNN', 'CNN-LSTM'});




