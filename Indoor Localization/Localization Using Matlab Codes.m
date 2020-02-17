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
%% Step peak detection
% ut=0.5; lt=-0.5; th_step=0.5;
% % ut=0; lt=0; th_step=0;
% upper_th = ut*ones(size(dt2));
% lower_th = lt*ones(size(dt2));
% 
% maxima=NaN(size(dt2));
% minima=NaN(size(dt2));
% 
% maxtemp = 1; mintemp = 1;
% up_num = 0; low_num = 0;
% up_flag = 0; low_flag = 0;
% for kg = 1 : length(acc_amp)
%     if lp_filtered(kg)>upper_th(kg)
%         if up_flag == 0
%             low_flag = 0;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
%             up_num = up_num+1;
%             maxtemp(up_num)=kg;
%             maxima(kg) = lp_filtered(kg);
%             up_flag = 1;
%         else
%             low_flag = 0;
%             if maxima(maxtemp(up_num)) < lp_filtered(kg)
%                 maxima(maxtemp(up_num)) = NaN;
%                 maxtemp(up_num) = kg;
%                 maxima(kg) = lp_filtered(kg);
%             end
%         end
%         
%         if up_num ~= 0
%             if (dt2(kg)-dt2(maxtemp(up_num)))>0.5
%                 maxima(maxtemp(up_num)) = NaN;
%                 maxtemp(up_num) = NaN;
%                 up_num = up_num -1;
%                 up_flag = 0;
%                 lowerflag = 0;
%             end
%         end
%     elseif lp_filtered(kg) < lower_th(kg)
%         if low_flag == 0
%             up_flag = 0;
%             low_flag = 1;
%             low_num = low_num + 1;
%             mintemp(low_num) = kg;
%             minima(kg) = lp_filtered(kg);
%         else
%             up_flag = 0;
%             if minima(mintemp(low_num)) > lp_filtered(kg)
%                 minima(mintemp(low_num)) = NaN;
%                 mintemp(low_num) = kg;
%                 minima(kg) = lp_filtered(kg);
%             end
%         end
%     end
% %     up_num
% %     low_num
% end
% if up_num>low_num
%     step_est = low_num;
% else
%     step_est = up_num;
% end
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
%% pitch and roll from Acc
% g = 9.8;
% for q =  2: length(dt2) 
%  %pitch
%     theta_acc(q) = -atan2(acc(q,1),sqrt(acc(q,2)^2+acc(q,3)^2));%asin(acc(i,2)./g);   %atan2(acc(i,1),sqrt(acc(i,2)^2+acc(i,3)^2));   asin(acc(i,1)/g);%
%     %roll
%     phi_acc(q) =   atan2(acc(q,2),acc(q,3));%atan2(acc(i,2),sqrt(acc(i,1)^2+acc(i,3)^2)); %asin(-acc(i,2)/(g*cos(theta_acc(i))));%
%     psi_acc(q)=0;
% end
% %%
% for W = 1 : length(phi_acc)
%   
%  % euler to Quatern<ion (scalar, vector)
%     quat_Acc(:,W) = [cos(psi_acc(W)/2)*cos(theta_acc(W)/2)*cos(phi_acc(W)/2)+sin(psi_acc(W)/2)*sin(theta_acc(W)/2)*sin(phi_acc(W)/2);
%         cos(psi_acc(W)/2)*cos(theta_acc(W)/2)*sin(phi_acc(W)/2)-sin(psi_acc(W)/2)*sin(theta_acc(W)/2)*cos(phi_acc(W)/2);
%         cos(psi_acc(W)/2)*sin(theta_acc(W)/2)*cos(phi_acc(W)/2)+sin(psi_acc(W)/2)*cos(theta_acc(W)/2)*sin(phi_acc(W)/2);
%         sin(psi_acc(W)/2)*cos(theta_acc(W)/2)*cos(phi_acc(W)/2)-cos(psi_acc(W)/2)*sin(theta_acc(W)/2)*sin(phi_acc(W)/2)];
% end
% 
% %% kalman filter for
% p = gyro_qat2(:,1); q = gyro_qat2(:,2); r = gyro_qat2(:,3);
% x_up(:,1) = [1, 0, 0, 0];
% cov_p_up(:,:,1) = eye(4);
% cov_q = 0.001*eye(4);
% cov_r =0.0001*eye(4);% 0.001*eye(4);
% h_mat = 1*eye(4);
% omega(:,:,1) = [0 -p(1) -q(1) -r(1); p(1) 0 r(1) -q(1); q(1) -r(1) 0 p(1); r(1) q(1) -p(1) 0];
% for e = 2 : length(quat_Acc(1,:))
%     
%     %% Prediction
%     omega(:,:,e) = [0 -p(e) -q(e) -r(e); p(e) 0 r(e) -q(e); q(e) -r(e) 0 p(e); r(e) q(e) -p(e) 0];
%     a_mat(:,:,e) = eye(4)+omega(:,:,e-1)*dt(e-1)/2;
%     x_hat(:,e) = a_mat(:,:,e)*x_up(:,e-1);
%     cov_p(:,:,e) = a_mat(:,:,e)*cov_p_up(:,:,e-1)*a_mat(:,:,e)'+cov_q;
%        a(:,:,e) = inv(h_mat*cov_p(:,:,e)*h_mat'+cov_r);
%     gain(:,:,e) = cov_p(:,:,e)*h_mat*a(:,:,e);
%     x_up(:,e) = x_hat(:,e) + gain(:,:,e)*(quat_Acc(:,e)-h_mat*x_hat(:,e));    
%     cov_p_up(:,:,e) = cov_p(:,:,e)-gain(:,:,e)*h_mat*cov_p(:,:,e);
% end
% for e = 1 : length(x_up(1,:)) 
%     phi_kalman(e) = atan2(2*(x_up(1,e)*x_up(2,e)+x_up(3,e)*x_up(4,e)),1-2*(x_up(2,e)^2+x_up(3,e)^2));
%     theta_kalman(e) = asin(2*(x_up(1,e)*x_up(3,e)-x_up(4,e)*x_up(2,e)));
%     psi_kalman(e) = atan2(2*(x_up(1,e)*x_up(4,e)+x_up(2,e)*x_up(3,e)),1-2*(x_up(3,e)^2+x_up(4,e)^2));
% end
%% Gyro euler angle
% phi_eul = 0; theta_eul =0; psi_eul = 0;
% for y = 2 : length(dt2)
%     phi_eul(y) = phi_eul(y-1)+dt2(y)*(gyro_raw2(y,1) + gyro_raw2(y,2)*sin(phi_eul(y-1))*tan(theta_eul(y-1)) + gyro_raw2(y,3)*cos(phi_eul(y-1))*tan(theta_eul(y-1)));
%     theta_eul(y) = theta_eul(y-1)+dt2(y)*(gyro_raw2(y,2)*cos(phi_eul(y-1)) - gyro_raw2(y,3)*sin(phi_eul(y-1)));
%     psi_eul(y) = psi_eul(y-1)+dt2(y)*(gyro_raw2(y,2)*sin(phi_eul(y-1))*sec(theta_eul(y-1)) + gyro_raw2(y,3)*cos(phi_eul(y-1))*sec(theta_eul(y-1)));
% end 
%%
% if d==20    %=====ADDed
% phi_gyro2(1) = 0;
% theta_gyro2(1) = 0;
% psi_gyro2(1) = 0;
% end         %====ADDed
% 
% for f = 2 : length(gyro_raw2(:,1))
%     phi_gyro2(f) = phi_gyro2(f-1)+gyro_raw2(f,1)*dt2(f);
%     theta_gyro2(f) = theta_gyro2(f-1)+gyro_raw2(f,2)*dt2(f);
%     psi_gyro2(f) = psi_gyro2(f-1)+gyro_raw2(f,3)*dt2(f);
% end

%%
q0=gyro_qat2(:,1);%-0.4525;
q1=gyro_qat2(:,2);%+0.4139;
q2=gyro_qat2(:,3);%-0.3509;
q3=gyro_qat2(:,4);%-0.7076;
%%
 psi_gyro2=atan2(2*(q1.*q2+q0.*q3),(q0.^2+q1.^2-q2.^2-q3.^2));

 
%   psi_gyro2=atan(2*(q1.*q2+q0.*q3)./(q0.^2+q1.^2-q2.^2-q3.^2));
%offset calculation

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
%       position_yw= position_yw(:,end);
%          dt2=dt2(:,end);

 end
% clc
 
end

