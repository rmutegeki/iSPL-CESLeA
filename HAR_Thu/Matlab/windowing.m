%% Windowing
% Cutting and labelling windows for all experiments' data
% Data description: 
% combined_data (dtype: column cell). Each cell is a (no. samples x A)
% array where: (A - 1) first columns are Acc, Gyr, ... signals
%              the last column is label
% Activities:   3 Basic activities: Standing - 1
%                                   Sitting - 2
%                                   Walking - 3
%               6 Transitions: stand-to-walk - 4
%                              stand-to-sit - 5
%                              sit-to-stand - 6
%                              walk-to-stand - 7
%                              sit-to-walk - 8
%                              walk-to-sit - 9
%%
% clc; clear; close all;
% load combined_raw_data.mat


combined_data = combined_raw_data;
% combined_data = combined_filtered_data;
window_length = 256;
overlap = 128;
num_sig = 45 % number of sensor signals will be chosen

num_exp = size(combined_data, 1);   % Number of experiments
Window_data = {};   % a cell: each row of Window_data contains the data of a window
window_labels = [];  % a vector contains the label of windows

for i = 1 : num_exp
    fprintf('================= experiment %d\n', i)
    exp_data = combined_data{i}(:, 1:num_sig);
    exp_label = combined_data{i}(:, size(combined_data{i}, 2));
    
    
%%     % (BASIC ACTIVITIES ONLY)
%     % Re-labelling activities: replace all transitions by their start and
%     % end activities.
%     % If using transitions, please comment this part.
%     isTran = 0;
%     start_act = 0;
%     end_act = 0;    
%     start_point = 0;
%     end_point = 0;
%     mid_point = 0;
%     
%     for i2 = 1 : size(exp_data, 1)
%         if (isTran == 0) && (exp_label(i2) >= 4) % start of transition
%             isTran = 1;
%             start_act = exp_label(i2 - 1);
%             start_point = i2;
% %             fprintf('start_act = %d\n', start_act)
% %             fprintf('start_point = %d\n', start_point)
%         end
%         
%         if (isTran == 1) && (exp_label(i2) < 4) % end of transition
%             isTran = 0; % reset
%             end_act = exp_label(i2);
%             end_point = i2 - 1;
%             mid_point = floor((end_point - start_point)/2 + start_point);
%             exp_label(start_point : mid_point) = start_act * ones(mid_point - start_point + 1, 1);
%             exp_label(mid_point+1 : end_point) = end_act * ones(end_point - mid_point, 1);
%             
% %             fprintf('mid_point = %d\n', mid_point)
% %             fprintf('end_act = %d\n', end_act)
% %             fprintf('end_point = %d\n', end_point)
%         end       
%     end
% %     fprintf('========= unique(exp_label)\n')
%     unique(exp_label)
%%    % End of Re-labelling
    
    %% Cutting raw data into windows and labelling those windows
    
    for i2 = 1 : (window_length - overlap) : (size(exp_data, 1) - window_length + 1)
        Window_data = [Window_data; exp_data(i2 : i2+window_length-1, :)];
        window_labels = [window_labels; mode(exp_label(i2 : i2+window_length-1))];
        
    end
    
    
end

% Reshape and save data in txt file 
for i = 1: size(Window_data,1)
    X(i, :) = reshape(Window_data{i}, [1, window_length * num_sig]);
end
X = array2table(X);
% writetable(X,'Window_data.txt');

% save('BasicAct\Window_data.mat', 'Window_data', 'window_labels');
% save('Transition\Window_data.mat', 'Window_data', 'window_labels');



