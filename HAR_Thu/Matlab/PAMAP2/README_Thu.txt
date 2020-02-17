
1. PAMAP2_preprocessing.m: Process the data of 1 IMU attached to hand
5 steps:
- Step 1: 
	+ Import the data from the folder "Protocol" and "Optional"
	+ Select the necessary data: time, activity ID, IMU1, IMU2, IMU3
	+ Save the data to "combined_raw_3IMUs.mat", a cell array, where each cell is 1 experiment contains the following information:
		- 1: timestamp
		- 2: activityID
		- 3-5: Acc (Hand)
		- 6-8: Gyro (Hand)
		- 9-11: Mag (Hand)
		- 12-20: Acc, Gyro, Mag (Chest)
		- 21-29: Acc, Gyro, Mag (Ankle)
- Step 2:
	+ Take only the Acc and Gyr signal from the IMU attached to hand (1st IMU)
	+ Downsampling from 100Hz to 50Hz
- Step 3:
	+ Remove unidentified activities' data (the activities that have ID = 0)
	+ Add a flag between those gaps
- Step 4:
	+ Replace NaN values in the data by interpolation (using mean value of the previous and the next time step)
- Step 5:
	+ Cut data into windows

* After 5 steps, the final outputs are: combined_label: 1x14 cell
					combined_window: 1x14 cell

2. change_label.m
The outputs of "PAMAP2_preprocessing.m" will be input to the "change_label.m" because the label of activities are not continuous
	+ Change the label of activities 
	+ Merge all the experiments from a cell array into 1 2-D array 
	+ Convert the above merged array to txt for using in Python
* Output: 

3. ADDITION: PAMAP2_preprocessing2.m: Similar to PAMAP2_preprocessing.m but using all 3 IMU sensors instead of only using the one attached on hand.
	  
