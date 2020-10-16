data1 = rawdata20200403145723sensor1;
data2 = rawdata20200403145726sensor2;
data3 = rawdata20200403145728sensor3;
difference = {};
for i = 1: length(data1)-1
difference{1}(i) = data1(i+1,1) - data1(i,1);
end
for i = 1: length(data2)-1
difference{2}(i) = data2(i+1,1) - data2(i,1);
end
for i = 1: length(data3)-1
difference{3}(i) = data3(i+1,1) - data3(i,1);
end
diff = {};
for i = 1: length(data1)-1
diff{1}(i) = data1(i+1,2) - data1(i,2);
end
for i = 1: length(data2)-1
diff{2}(i) = data2(i+1,2) - data2(i,2);
end
for i = 1: length(data3)-1
diff{3}(i) = data3(i+1,2) - data3(i,2);
end
mean(diff{1}(:))
mean(diff{2}(:))
mean(diff{3}(:))
figure; title("Millisecond"); subplot(311); stem(diff{1}(:)); hold on;
subplot(312); stem(diff{2}(:)); hold on;
subplot(313); stem(diff{3}(:));
figure; title("Time steps"); subplot(311); stem(difference{1}(:)); hold on;
subplot(312); stem(difference{2}(:)); hold on;
subplot(313); stem(difference{3}(:));