clear all; clc;
close all;
instrfind();
delete(instrfindall);
set = serial('COM3','BaudRate',921600);
  fopen(set);
figure
xlabel('X Position (m)');
ylabel('Y Position (m)');
hold on
d=200;
i=0;
j=200;
rr=1;
c=200;



 position_yw(1,1) = 10;
  position_yw(2,1) = 10;


qq=1;
while(1) 
%%

i = i +1;
    data1 = str2num(fscanf(set));
     data2(i,:)=data1;
    time(i,:) = str2num(datestr(now,'HH,MM,SS.FFF'));
    if i >1
        if time(i,1) == time(i-1,1)        
            if time(i-1,2) < time(i,2) && time(i-1,1) <= time(i,1)
                dt(i) = (time(i,2)-time(i-1,2))*60+(time(i,3)-time(i-1,3));
            elseif time(i-1,2) < time(i,2) && time(i-1,1) > time(i,1)
                dt(i) = (time(i,2)-time(i-1,2))*60-(time(i,3)-time(i-1,3));
            else
                dt(i) = time(i,3)-time(i-1,3);
            end
        else
            if time(i-1,1) <= time(i,1)
                dt(i) = (time(i,2)+60-time(i-1,2))*60 + (time(i,3)-time(i-1,3));
            else
                dt(i) = (time(i,2)+60-time(i-1,2))*60 - (time(i,3)-time(i-1,3));
            end
        end
    end 
      if floor(i/50) ~= floor((i-1)/50)
        sec = floor(i/50)
      end 
    gyro_qat(i,1) = data1(2);%/180*pi;
    gyro_qat(i,2) = data1(3);%/180*pi;
    gyro_qat(i,3) = data1(4);%/180*pi;
    gyro_qat(i,4) = data1(5);%/180*pi;
    acc_raw(i,1) = data1(9);
    acc_raw(i,2) = data1(10);
    acc_raw(i,3) = data1(11);
    mag_raw(i,1) = data1(12);
    mag_raw(i,2) = data1(13);
    mag_raw(i,3) = data1(14);
 
    

if d==i
%     fclose (se);
     raw_data = data2(rr:c,:);
     dt2 = dt(rr:c);
     gyro_qat2 =gyro_qat(rr:c,:); 
     acc_raw2 = acc_raw(rr:c,:); 
     mag_raw2 = mag_raw(rr:c,:);   
     M = 201; 
%% Moving Average, acc   
acc(1:(M-1)/2,1:3) = acc_raw2(1:(M-1)/2,1:3);
acc(length(acc_raw2(:,1))-(M-1)/2+1:length(acc_raw2(:,1)),1:3) = acc_raw2(length(acc_raw2(:,1))-(M-1)/2+1:length(acc_raw2(:,1)),1:3);
for z = 1 : length(acc_raw2(:,1))-(M-1)
    acc(z+(M-1)/2,1:3) = sum(acc_raw2(z:z+M-1,1:3))/M;
end


%% Filtering
   alpha = 0.9;
   hp_avg = 0;
   
for h = 1 : length(acc_raw2(:,1))
    acc_amp(h) = norm(acc_raw2(h,1:3));
end
hp_filtered = zeros(1,length(acc_raw2(:,1)));
for h = 1 : length(acc_raw2(:,1))
    hp_avg = acc_amp(h)*(1-alpha)+hp_avg*alpha;
    hp_filtered(h) = acc_amp(h)-hp_avg;
end
lp_filtered(1:(M-1)/2) = hp_filtered(1:(M-1)/2);
lp_filtered(length(acc_raw2(:,1))-(M-1)/2+1:length(acc_raw2(:,1))) = hp_filtered(length(acc_raw2(:,1))-(M-1)/2+1:length(acc_raw2(:,1)));

for k = 1 : length(acc_raw2(:,1))-(M-1)
    lp_filtered(k+(M-1)/2) = sum(hp_filtered(k:k+M-1))/M;
end


[pks,locs] =findpeaks(lp_filtered,'MinPeakHeight',0.1);
step_est=length(locs);
%% Step`n   
step_size = zeros(1,step_est);
kk = 0.5;
len = zeros(1,step_est);
for h = 1 : step_est-1 %Kim Approach
    step_size_sum = sum(abs(lp_filtered(locs(h):locs(h+1))));
    len = locs(h+1)-locs(h);
    step_size(h) = kk * nthroot(step_size_sum/len,3);
end


%%
q0=gyro_qat2(:,1);%-0.4525;
q1=gyro_qat2(:,2);%+0.4139;
q2=gyro_qat2(:,3);%-0.3509;
q3=gyro_qat2(:,4);%-0.7076;
%%
 psi_gyro2=atan2(2*(q1.*q2+q0.*q3),(q0.^2+q1.^2-q2.^2-q3.^2));

 

%% Position detection algorithm

if qq==1
    headng= zeros(2,length(step_size)-1);
   for o = 1 : length(locs)-1
      headng(o) = mean(psi_gyro2(locs(o):locs(o+1)));   
   end 
headng
else
%       psi_gyro2= psi_gyro2(end);
%     gama= gama(:,end);
%     headng= headng(:,end);
    for o = 1 : length(locs)-1
      headng(o) = mean(psi_gyro2(locs(o):locs(o+1)));
      
    end
headng 
end

% headng 
if qq==1

    position_yw = zeros(2,length(step_size)-1);
    
    for o= 2 : length(step_size)
       position_yw(1,o) = position_yw(1,o-1)+step_size(o)*cos( headng(o-1));
       position_yw(2,o) = position_yw(2,o-1)+step_size(o)*sin( headng(o-1));
    end

else

     position_yw = position_yw(:,end);
     
     for o = 2 : length(step_size)
       position_yw(1,o) = position_yw(1,o-1)+step_size(o)*cos( headng(o-1));
       position_yw(2,o) = position_yw(2,o-1)+step_size(o)*sin( headng(o-1));
       %if naming ==0

       %end
     end
     
end

position_yw

    plot(position_yw(1,:),position_yw(2,:),'*k');
    drawnow;
%end
    qq

    d=d+j;
 %i=j+1;
  rr=rr+j;
  c=c+j;
 qq=qq+1;
 
%  d=0;
      psi_gyro2= psi_gyro2(:,end);
      headng= headng(:,end);

 end
% clc
 
end

