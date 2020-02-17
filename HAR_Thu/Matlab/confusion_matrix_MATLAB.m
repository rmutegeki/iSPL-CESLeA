%%%%%%%%%% CONFUSION MAXTRIX %%%%%%%%%%%
% This file draws confusion matrix from the predY and testY files extracted
% from the python models

%% 1: Load the predy.txt and testy.txt files
load('testy.txt')
load('predy.txt')
% testy = testyCA;
% predy = predyCA;

%% 2: Categorize the data; ex: B = categorical(A,[1 2 3],{'red' 'green' 'blue'})
cat_labels = {'WALKING' 'WALKING UPSTAIRS' 'WALKING DOWNSTAIRS' 'SITTING' 'STANDING' 'LAYING'};
num_labels = [0 1 2 3 4 5];
% cat_labels = {'WALKING' 'STANDING' 'SITTING' 'LAYING' 'RESTING (SITTING)' 'USING PHONE (SITTING)' 'GIVING PRESENTATION' 'MEETING (SITTING)' 'WORKING WITH COMPUTER (SITTING)'};
% num_labels = [0 1 2 3 4 5 6 7 8];
y_pred = categorical(predy, num_labels, cat_labels);
y_test = categorical(testy, num_labels, cat_labels);

%% 3: plot confusion matrix
figure;
plotconfusion(y_test, y_pred, '12 activities - LSTM')
figure;
cm = confusionchart(y_test, y_pred,...
'ColumnSummary','column-normalized',...
'RowSummary','row-normalized',...
'FontSize', 14,...
'Title', '8 Activities - LSTM');