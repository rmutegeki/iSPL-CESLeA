function [Window_data, window_labels] = cutData_v3(X, Labels, window_length, overlap)
%CUTDATA_V3 cuts the data X into windows and labels those windows with the
%corresponding activities.
%   [window_data, window_label] = CUTDATA_V3(X, Label, window_length, overlap) 
%   - window_length is the length of each window
%   - X is a matrix where each row contains the acceleration and gyroscope
%   data of 1 time step
%   - overlap = (window_length - step length) is the overlap  between 2 adjacent windows.
%   - Label is a matrix with 5 columns: 
%           1st column: experiment ID, 
%           2nd column: user ID,
%           3rd column: activity ID (label)
%           4th column: starting point of that activity
%           5th column: ending point of that activity
%   Window_data is a cell with size of (number of windows) x 1:
%           each row is a windowed data (size: window_length x 6...no. Acc and Gyro)
%   window_label is column vector contains labels of the corresponding windows
%
% This version is the version 3 of cutData. CUTDATA_V3 deals with the
% gaps (like cutData_v2) AND breaks transitions into basic activities.
% DETAILS: label = 7 (Stand-to-Sit): divide the signal of Stand-to-Sit into
% 2 equal parts, the 1st part is Stand and the 2nd part is Sit. 
%
% 1 WALKING           
% 2 WALKING_UPSTAIRS  
% 3 WALKING_DOWNSTAIRS
% 4 SITTING           
% 5 STANDING          
% 6 LAYING            
% 7 STAND_TO_SIT      
% 8 SIT_TO_STAND      
% 9 SIT_TO_LIE        
% 10 LIE_TO_SIT        
% 11 STAND_TO_LIE      
% 12 LIE_TO_STAND 

num_act = 6; % Number of basic activities (not contain transitions)
Lab_X = [];
labels = [];
for i = 1 : size(Labels,1)
    start_point = Labels(i, 4);
    end_point = Labels(i, 5);
    middle_point = floor((end_point - start_point)/2) + start_point;
    start_label = Labels(i, 3);     
    end_label = Labels(i, 3);
    
    
    switch Labels(i, 3)
        case 7  % STAND_TO_SIT
            start_label = 5;
            end_label = 4;
        case 8  % SIT_TO_STAND
            start_label = 4;
            end_label = 5;
        case 9  % SIT_TO_LIE
            start_label = 4;
            end_label = 6;
        case 10  % LIE_TO_SIT
            start_label = 6;
            end_label = 4;
        case 11  % STAND_TO_LIE
            start_label = 5;
            end_label = 6;
        case 12  % LIE_TO_STAND
            start_label = 6;
            end_label = 5;
        otherwise
           
    end
    
    labels = [labels; start_label * ones(middle_point - start_point + 1, 1)
                    ; end_label * ones(end_point - middle_point, 1)];
    
    Lab_X = [Lab_X; X(start_point : end_point, :)];
    
    % check whether there is a gap or not
    if (i < size(Labels,1)) && (end_point + 1 ~= Labels(i+1, 4))
        
        % add a new data point as a flag
        labels = [labels; -1];
        Lab_X = [Lab_X; [0 0 0 0 0 0]];
    end
end

%% WINDOWING and LABELLING %%%%%%%%%


Window_data = {}; % type: cell
window_labels = [];

win_idx = 0; % window's index
i = 1;

while i <= (size(Lab_X, 1) - window_length)
    is_flag = false;
    flag_idx = 0;
    for i2 = i : (i + window_length - 1)
        if labels(i2) == -1 % have a gap in this window
            is_flag = true;
            flag_idx = i2;
            break
        end
    end
    if is_flag == true
        i = flag_idx + 1;
    else 
        win_idx = win_idx + 1;
        Window_data{win_idx} = Lab_X(i : i+window_length-1, :);
        window_labels(win_idx) = mode(labels(i : i+window_length-1)); % finding the most common label in the window
        i = i + (window_length - overlap);
    end        
end

%%

Window_data = Window_data';
window_labels = window_labels';

% =========================================================================
end
