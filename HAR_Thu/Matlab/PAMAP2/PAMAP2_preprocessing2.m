%%% PAMAP2: preprocessing 2 %%%
% This code describes the step-by-step of preprocessing part for 3 IMU
% sensors.
%% Works:
%   - Get the necessary information
%   - Need to remove all the unidentified activity sample
%   - Mark a flag there, so we will not merge those discrete together when
%   we do windowing
%   - Interpolation some NaN values

clear; clc; close all
%% STEP 1:
% % Import the data from the folder "Protocol"
% % Select the necessary data from the original PAMAP2:
% sub101 = subject101(:,[1 2 5:7 11:16 22:24 28:33 39:41 45:50]);
% % "combined_raw_3IMUs .mat" is a cell array, each cell contains the data,
% of 1 subject (or 1 experiment)
% % The structure of 3IMUs data sub101 (1 experiment):
% % - 1: timestamp
% % - 2: activityID
% % - 3-5: Acc (Hand)
% % - 6-8: Gyro (Hand)
% % - 9-11: Mag (Hand)
% % - 12-20: Acc, Gyro, Mag (Chest)
% % - 21-29: Acc, Gyro, Mag (Ankle)
load('Data\3_IMUs\combined_raw1_3IMUs.mat')

%% STEP 2:
% Only take the Acc and Gyr signal from the 3 IMUs, and down sampling from ~100HZ to 50Hz
combined_raw2_3IMUs = {};    % the number 2 here means the data obtained in step 2
for i = 1 : size(combined_raw_3IMUs, 2)     % size of combined_raw_3IMUs: [1, num_experiments]
    sub = [];
    sub = combined_raw_3IMUs{i}(:,[2:8 12:17 21:26]);
    sub = downsample(sub,2);
    combined_raw2_3IMUs{i} = sub;
end
% save('Data\3_IMUs\combined_raw2_3IMUs.mat','combined_raw2_3IMUs')
% % structure of 1 cell in combined_raw2_1IMU:
% % 1: activity ID
% % 2-4: Acc, 5-7: Gyr (HAND)
% % 8-10: Acc, 11-13: Gyr (CHEST)
% % 14-16: Acc, 17-19: Gyr (ANKLE)

%% STEP 3:
% Remove unidentified activities' data and put a flag between those gaps
combined_raw3_3IMUs = {};    % combined raw data at step 3
k = 0;
flag = 0;
for i1 = 1:size(combined_raw2_3IMUs,2)
    temp_cell = combined_raw2_3IMUs{i1};
    data = [];
    k = 0;
    flag = 0;
    for i2 = 1:size(temp_cell,1)
        if temp_cell(i2,1) > 0
            k = k + 1;
            data(k,:) = temp_cell(i2,:);
            if i2 < size(temp_cell,1) && temp_cell(i2+1,1) == 0
                % add a flag (-1, -1, -1,...)
                k = k + 1;
                data(k,:) = - ones(1, size(temp_cell,2));
            end
        end
    end
    combined_raw3_3IMUs{i1} = data;
end
% clear combined_raw2_3IMUs temp_cell    % deallocating memory

%             
% data = [];
% k = 0;
% flag = 0;
% for i = 1:size(sub,1)
%     if sub(i,1) > 0
%         k = k+1;
%         data(k,:) = sub(i,:);
%         if i < size(sub,1) && sub(i+1,1) == 0
%             % add a flag (-1, -1, -1,...)
%             k = k + 1;
%             data(k,:) = - ones(1, size(sub,2));
%         end
%     end
% end
% clear sub  % deallocating memory


%% STEP 4:
% There are NaN values in the data so we need to remove them and use
% interpolation to fill out in those blanks by taking the mean of the previous
% and the next time step.
% Or fill out those blanks by the following time step (only for the 1st row)
% or the previous time step (otherwise)
combined_raw4_3IMUs = {};
for i1 = 1:size(combined_raw3_3IMUs,2)
    temp_cell = combined_raw3_3IMUs{i1};
    for i2 = 1:size(temp_cell,1)
        for i3 = 2:size(temp_cell,2)
            if isnan(temp_cell(i2,i3))
                if i2 == 1      % case: the NaN is at the 1st row, then find the nearest non-NaN element
                    for i4 = 2:size(temp_cell,1)
                        if ~isnan(temp_cell(i4,i3))
                            temp_cell(i2,i3) = temp_cell(i4,i3);
                            break
                        end
                    end
                else temp_cell(i2, i3) = temp_cell(i2-1, i3);
                end
                
                
                %if isnan(temp_cell(i2+1,i3))    % dealing with the case there are 2 consecutive NaN
                    %temp_cell(i2,i3) = temp_cell(i2-1, i3);
                %else
                    %temp_cell(i2,i3) = mean([temp_cell(i2-1, i3) temp_cell(i2+1, i3)]);
                %end
            end
        end
    end
    combined_raw4_3IMUs{i1} = temp_cell;
end
% clear temp_cell combined_raw3_3IMUs
     
% for i = 1:size(data,1)
%     for j = 2:size(data,2)
%         if isnan(data(i,j))
%             data(i,j) = mean([data(i-1, j) data(1+1, j)]);
%         end
%     end
% end

%% STEP 5:
% Windowing
win_len = 128*1.25;
overlap = win_len/2;
n_signal = 18;   % number of sensor signals: AccX, AccY, AccZ, GyrX, GyrY, GyrZ

combined_window = {};
combined_label = {};
for i1 = 1:size(combined_raw4_3IMUs,2)
    temp_cell = combined_raw4_3IMUs{i1};
    label = [];
    window = [];
    win_idx = 0;
    i2 = 1;
    while i2 <= (size(temp_cell,1) - win_len)
        is_flag = false;
        flag_idx = 0;
        for i3 = i2 : (i2 + win_len - 1)
            if temp_cell(i3, 1) == -1   % there is a gap in this window
                is_flag = true;
                flag_idx = i3;
                break
            end
        end
        if is_flag == true
            i2 = flag_idx + 1;
        else
            win_idx = win_idx + 1;
            window(win_idx,:) = reshape(temp_cell(i2 : i2+win_len-1, 2:size(temp_cell,2)),1,win_len*n_signal);
            label(win_idx) = mode(temp_cell(i2 : i2+win_len-1, 1)); % finding the most common label in the window
            i2 = i2 + (win_len - overlap);
        end
    end
    combined_window{i1} = window;
    combined_label{i1} = label;
end
% save('3_IMUs_window_'xyz'.mat','combined_label','combined_window')  % where 'xyz' is the window size


% label = [];
% window = []; % flatten the window from (n_win, win_len, n_signal) to (n_win, win_len*n_signal)
% win_idx = 0;
% i = 1;
% while i <= (size(data,1) - win_len)
%     is_flag = false;
%     flag_idx = 0;
%     for i2 = i : (i + win_len - 1)
%         if data(i2, 1) == -1  % have a gap in this window
%             is_flag = true;
%             flag_idx = i2;
%             break
%         end
%     end
%     if is_flag == true
%         i = flag_idx + 1;
%     else
%         win_idx = win_idx + 1;
%         window(win_idx,:) = reshape(data(i : i+win_len-1, 2:size(data,2)),1,win_len*n_signal);
%         label (win_idx) = mode(data(i : i+win_len-1, 1)); % finding the most common label in the window
%         i = i + (win_len - overlap);
%     end
% end
% 
% % (Need to change the file name) before saving
% window14 = window; 
% label14 = label';
% save('data14.mat', 'label14', 'window14')