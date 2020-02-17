%% Change the label of PAMAP2 and then merge all the experiment into 1 file, also convert to txt file for using in python
% Because the label are not continuous:
% – 1 lying
% – 2 sitting
% – 3 standing
% – 4 walking
% – 5 running
% – 6 cycling
% – 7 Nordic walking
% – 9 watching TV               9  => 8
% – 10 computer work            10 => 9
% – 11 car driving              11 => 10
% – 12 ascending stairs         12 => 11
% – 13 descending stairs        13 => 12
% – 16 vacuum cleaning          16 => 13
% – 17 ironing                  17 => 14
% – 18 folding laundry          18 => 15
% – 19 house cleaning           19 => 16
% – 20 playing soccer           20 => 17
% – 24 rope jumping             24 => 18

% NOTE: the official data only contains 12 first activities, from window 1
% to window 15.006 (with window_size = 128)
clc; clear; close all
load('Data\3_IMUs\3_IMUs_window_256.mat')

%% Change the labels (activity ID)
for i1 = 1:size(combined_label,2)
    for i2 = 1:size(combined_label{i1},2)
        if 9 <= combined_label{i1}(i2) && combined_label{i1}(i2) <= 13
            combined_label{i1}(i2) = combined_label{i1}(i2) - 1;
        end
        if 16 <= combined_label{i1}(i2) && combined_label{i1}(i2) <= 20
            combined_label{i1}(i2) = combined_label{i1}(i2) - 3;
        end
        if combined_label{i1}(i2) == 24
            combined_label{i1}(i2) = 18;
        end
    end
end

%% Merge all the experiments
merged_window = [];
merged_label = [];
for i1 = 1:size(combined_window,2)
    for i2 = 1:size(combined_window{i1},1)
        merged_window = [merged_window; combined_window{i1}(i2,:)];
        merged_label = [merged_label; combined_label{i1}(i2)];
    end
end

            
% save('1_IMU_window_'xyz'.mat','combined_label','combined_window')  % where 'xyz' is the window size
% save('1_IMU_merged_data_'xyz'.mat','merged_label','merged_window')  % where 'xyz' is the window size
% writematrix(merged_window,'window_'xyz'.txt','Delimiter','tab')
% writematrix(merged_label,'label_'xyz'.txt','Delimiter','tab')


% load('D:\THU\isp-lab\HAR\code\matlab\PAMAP2_Dataset\Data\1_IMU\combined_data.mat')
% for i = 1 : size(label,1)
%     if 9 <= label(i) && label(i) <= 13
%         label(i) = label(i) - 1;
%     end
%     if 16 <= label(i) && label(i) <= 20
%         label(i) = label(i) - 3;
%     end
%     if label(i) == 24
%         label(i) = 18;
%     end
% end
%
% save('combined_data.mat', 'window','label')
% %% Save to txt files for python
% writematrix(window,'window.txt','Delimiter','tab')
% writematrix(label,'label.txt','Delimiter','tab')
% 
% %% Plot histogram
% x = categorical({'LYING', 'SITTING', 'STANDING', 'WALKING', 'RUNNING', 'CYCLING','NORDIC WALK',...
%     'WATCHING TV', 'COMPUTER WORK', 'CAR DRIVING', ' ASCENDING STAIR', 'DESCENDING STAIR',...
%     'VACUUM CLEANING', 'IRONING', 'FOLDING LAUNDRY','HOUSE CLEANING', 'PLAYING SOCCER', 'ROPE JUMPING'})
% x = reordercats(x, {'LYING', 'SITTING', 'STANDING', 'WALKING', 'RUNNING', 'CYCLING', 'NORDIC WALK',...
%     'WATCHING TV', 'COMPUTER WORK', 'CAR DRIVING', ' ASCENDING STAIR', 'DESCENDING STAIR',...
%     'VACUUM CLEANING', 'IRONING', 'FOLDING LAUNDRY','HOUSE CLEANING', 'PLAYING SOCCER', 'ROPE JUMPING'})
% y = []
% for i = 1:18
%     y(i) = size(find(label == i),1);
% end
% bar(x, y)