function [Window_data, window_labels] = cutData(X, Labels, window_length, overlap)
%CUTDATA cuts the data X into windows and labels those windows with the
%corresponding activities.
%   [window_data, window_label] = CUTDATA(X, Label, window_length, overlap) 
%   - window_length is the length of each window
%   - X is a matrix where each row contains the acceleration and gyroscope
%   data of 1 time step
%   - overlap is the overlap (or step length) between 2 adjacent windows.
%   - Label is a matrix with 5 columns: 
%           1st column: experiment ID, 
%           2nd column: user ID,
%           3rd column: activity ID (label)
%           4th column: starting point of that activity
%           5th column: ending point of that activity
%   Window_data is a cell with size of (number of windows) x 1:
%           each row is a windowed data (size: window_length x ...num of Acc and Gyro)
%   window_label is column vector contains labels of the corresponding windows
%
%
% The idea here is using the matrix Label to create a new matrix named 
% Lab_X which has the same length with the labelled data in Label 
% (because some parts of the signal X were not labelled).
% Lab_X will contain the data and label of activity along
% time. 
% Then we cut data into windows and label that window.
% For the case that there are more than 1 types of activities in a window,
% we will label the acitivity that has the most data points in that window


% Lab_X = zeros(data_size, size(X,2));
Lab_X = [];
label = [];
for i = 1 : size(Labels,1)
    start_point = Labels(i, 4);
    end_point = Labels(i, 5);
    
    label = [label; Labels(i, 3) * ones(end_point - start_point + 1, 1)];
    
    Lab_X = [Lab_X; X(start_point : end_point, :)];
end

% Now in Lab_X: n first column is Acc and Gyro data, the last column is
% label

%% WINDOWING and LABELLING %%%%%%%%%
Window_data = {}; % type: cell
window_labels = [];
j = 0;
size(Lab_X, 1);
for i = 1 : overlap : (size(Lab_X, 1) - window_length)
    j = j + 1;
    
    Window_data{j} = Lab_X(i : i+window_length-1, :);
    window_labels(j) = mode(label(i : i+window_length-1)); % finding the most common label in the window
end
%%

Window_data = Window_data';
window_labels = window_labels';

% =========================================================================
end
