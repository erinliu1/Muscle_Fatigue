import os
import pandas as pd
import numpy as np
from scipy.signal import welch, find_peaks
from scipy.fft import fft

def create_new_folder(directory, folder_name):
    """
    Create a new folder with leading zeros in the folder name.
    """
    directory = directory
    existing_folders = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    if not existing_folders:
        new_folder_name = f"{folder_name}_0001"
    else:
        last_numbers = [int(name.split('_')[-1]) for name in existing_folders if name.split('_')[-1].isdigit()]
        max_last_number = max(last_numbers) if last_numbers else 0
        
        new_last_number = max_last_number + 1

        # Generate folder name with leading zeros
        new_folder_name = f"{folder_name}_{new_last_number:04d}"

    folder_path = os.path.join(directory, new_folder_name)
    os.makedirs(folder_path)
    return folder_path

imu_lookup = {
    'arm': {
        'device_name': 'violet_IMU',
        'serial_number': '655782F7'
    },
    'wrist': {
        'device_name': 'green_IMU',
        'serial_number': '65577B49'
    }
}

def get_csv_df(folder_path, folder_type, imu, csv_name):
    """
    Given the folder_path to the participant's data
    - the folder_type argument should be either 'Baseline' or 'Fatigue'
    - the imu argument should be either 'wrist' or 'arm'. This will triger the imu_lookup and result in the proper folder for the wrist or arm IMU data.
    - the csv_name argument should be 'EulerAngles' or 'Inertial'

    Returns a Pandas DataFrame where the index is the timestamp in milliseconds since the beginning of the data collection. 
    """
    imu_name = imu_lookup[imu]['device_name']
    imu_serial_number = imu_lookup[imu]['serial_number']
    try:
        df = pd.read_csv(folder_path + f'/{folder_type}/{imu_name} {imu_serial_number} (UDP)/{csv_name}.csv')
    except:
        df = pd.read_csv(folder_path + f'/{folder_type}/{imu_name} {imu_serial_number} (TCP)/{csv_name}.csv')
    min_time = df['Timestamp (us)'].min()
    df['Timestamp (ms)'] = ((df['Timestamp (us)'] - min_time) / 1000)
    return df.drop(columns=['Timestamp (us)'])

def get_euler_df(folder_path, folder_type, imu):
    """
    Given the folder_path to the participant's data
        - the folder_type argument should be either 'Baseline' or 'Fatigue'
        - the imu argument should be either 'wrist' or 'arm'. This will triger the imu_lookup and result in the proper folder for the wrist or arm IMU data.
    
    Returns a Pandas DataFrame where the index is the timestamp in milliseconds since the beginning of the data collection. 
    """
    return get_csv_df(folder_path, folder_type, imu, 'EulerAngles')

def get_inertial_df(folder_path, folder_type, imu):
    """
    Given the folder_path to the participant's data
        - the folder_type argument should be either 'Baseline' or 'Fatigue'
        - the imu argument should be either 'wrist' or 'arm'. This will triger the imu_lookup and result in the proper folder for the wrist or arm IMU data.
    
    Returns a Pandas DataFrame where the index is the timestamp in milliseconds since the beginning of the data collection. 
    """
    return get_csv_df(folder_path, folder_type, imu, 'Inertial')

def get_euler_difference(euler_df_wrist, euler_df_arm):
    """
    Given the Pandas DataFrames for the EulerAngles of the wrist and arm:
    - Synchronize the timestamps of the two measurements (we will be using the timestamp from 'euler_df_wrist')
    - Compute the difference of between the 'euler_df_arm' values and the 'euler_df_wrist' values for each timestamp
    - return the resulting DataFrame
    """
    euler_difference = {
        'Timestamp (ms)' : [],
        'Roll (deg)' : [],
        'Pitch (deg)' : [],
        'Yaw (deg)' : [],
    }
    for i in range(min(len(euler_df_arm), len(euler_df_wrist))):
        for key, val_arm in euler_df_arm.loc[i].to_dict().items():
            val_wrist = euler_df_wrist.loc[i].to_dict()[key]
            if key == 'Timestamp (ms)':
                euler_difference[key].append(val_wrist)
            else:
                euler_difference[key].append(val_arm - val_wrist)
    euler_difference_df = pd.DataFrame(euler_difference)
    return euler_difference_df

def get_mean_baseline(folder_path):
    """
    Given the folder_path to the participant's data, return the mean Euler angles from the Baseline measurement.
    """
    euler_df_wrist = get_euler_df(folder_path, 'Baseline', 'wrist')
    euler_df_arm = get_euler_df(folder_path, 'Baseline', 'arm')
    euler_difference_df = get_euler_difference(euler_df_wrist, euler_df_arm)
    return euler_difference_df.mean().to_dict()

def get_mean_baseline_pitch(folder_path):
    """
    Given the folder_path to the participant's data, return the average pitch value from the Baseline measurement.
    """
    return get_mean_baseline(folder_path)['Pitch (deg)']

def get_fatigue_euler_difference(folder_path):
    """
    Given the folder_path to the participant's data, return a Pandas DataFrame with the difference in values between the roll, pitch, and yaw of the arm imu and the wrist imu in the fatigue trial. The timestamps will be synchronized to the wrist imu.
    """
    euler_df_wrist = get_euler_df(folder_path, 'Fatigue', 'wrist')
    euler_df_arm = get_euler_df(folder_path, 'Fatigue', 'arm')
    return get_euler_difference(euler_df_wrist, euler_df_arm)

def below_baseline(pitch, baseline, i):
    return pitch[i] <= baseline and pitch[i-1] >= baseline

def above_baseline(pitch, baseline, i):
    return pitch[i] >= baseline and pitch[i-1] <= baseline

def get_repetition_intervals(pitch, baseline, timestamps):
    """
    Returns a list of tuples, containing the start and end milliseconds.
    """
    rise_indices = []
    sink_indices = []

    for i in range(0, len(pitch)):
        if below_baseline(pitch, baseline, i):
            sink_indices.append(i)
        elif above_baseline(pitch, baseline, i):
            rise_indices.append(i)
    trough_indices = []

    if len(rise_indices) == 0 or len(sink_indices) == 0:
        raise ValueError("Gurl your dumbbell repetitions never crossed the baseline pLEASE")
    
    # we want the first occurrence to be a sink. if it is a rise, then insert a sink at the very beginning. 
    if timestamps[rise_indices[0]] < timestamps[sink_indices[0]]:
        sink_indices.insert(0, 0)
    
    # we want the last occurrence to be a rise. if it is a sink, then insert a rise at the very end.
    if timestamps[rise_indices[-1]] < timestamps[sink_indices[-1]]:
        rise_indices.append(len(pitch)-1)

    # check to make sure the number of rise and sink indices match
    if len(rise_indices) != len(sink_indices):
        raise Exception("oh no erin what have u done")

    # compute troughs by looking in-between sinks and rises
    for i in range(len(rise_indices)):
        sink_i = sink_indices[i]
        rise_i = rise_indices[i]
        trough_indices.append((rise_i + sink_i)//2)
    
    # get the start the end points of each repetitions from consecutive troughs
    repetitions_indices = []
    repetitions_ms = []
    for i in range(len(trough_indices)-1):
        start_i = trough_indices[i]
        end_i = trough_indices[i+1]
        repetitions_indices.append((start_i, end_i))
        repetitions_ms.append((timestamps[start_i], timestamps[end_i]))
    return repetitions_ms

def get_borg_df(folder_path, timestamps):
    """
    Given the 'folder_path' to the participant's data, interpolate the borg results linearly according to the 'Timestamp (ms)' column in 'df_fatigue'.
    """
    df = pd.read_csv(folder_path + '/borg.csv', index_col=0, parse_dates=True)
    min_time = df.index.min()
    df.index = ((df.index - min_time).total_seconds() * 1000).rename('Timestamp (ms)')
    extra_indices = [i for i in list(df.index) if i not in list(timestamps)]
    df_reindexed = df.reindex(sorted(list(timestamps) + extra_indices))
    df_interpolated = df_reindexed.interpolate(method='linear')
    df_interpolated.drop(extra_indices, inplace=True)
    return df_interpolated

def get_repetition_df(repetition_intervals, df_borg):
    """
    For each repetition interval, given the interpolated borg dataframe, average the borg values and round it to the nearest integer or half. 
    Return a dataframe with the start and end times of the interval (in milliseconds), as well as the total length of the interval (in seconds) and the average rounded borg value.
    """
    start_ms, end_ms, average_borg = [], [], []
    for start, end in repetition_intervals:
        closest_start = df_borg.index[abs(df_borg.index - start).argmin()]
        closest_end = df_borg.index[abs(df_borg.index - end).argmin()]
        start_ms.append(closest_start)
        end_ms.append(closest_end)
        average_borg.append(round_borg(df_borg.loc[closest_start:closest_end]['fatigue'].mean()))
    df_repetitions = pd.DataFrame({'start (ms)':start_ms, 'end (ms)':end_ms, 'borg':average_borg})
    return df_repetitions

def round_borg(number):
    """
    Round a decimal to the nearest integer or half. 
    """
    rounded_integer = round(number)
    rounded_half = round(number * 2) / 2
    if abs(number - rounded_integer) < abs(number - rounded_half):
        rounded_value = rounded_integer
    else:
        rounded_value = rounded_half
    return rounded_value

def get_wrist_arm_imu_df(folder_path):
    euler_df_wrist = get_euler_df(folder_path, 'Fatigue', 'wrist')
    euler_df_arm = get_euler_df(folder_path, 'Fatigue', 'arm')
    inertial_df_wrist = get_inertial_df(folder_path, 'Fatigue', 'wrist')
    inertial_df_arm = get_inertial_df(folder_path, 'Fatigue', 'arm')

    if not inertial_df_wrist['Timestamp (ms)'].equals(euler_df_wrist['Timestamp (ms)']): 
        raise Exception('Wrist IMU euler and inertial measurements do not have same timestamps.')

    df_wrist = pd.merge(inertial_df_wrist, euler_df_wrist, on='Timestamp (ms)', how='inner')

    if not inertial_df_arm['Timestamp (ms)'].equals(euler_df_arm['Timestamp (ms)']): 
        raise Exception('Arm IMU euler and inertial measurements do not have same timestamps.')

    df_arm = pd.merge(inertial_df_arm, euler_df_arm, on='Timestamp (ms)', how='inner')

    all_data = {
        'Timestamp (ms)' : [],
        'Wrist Gyroscope X (deg/s)' : [],
        'Wrist Gyroscope Y (deg/s)' : [],
        'Wrist Gyroscope Z (deg/s)' : [],
        'Wrist Accelerometer X (g)' : [],
        'Wrist Accelerometer Y (g)' : [],
        'Wrist Accelerometer Z (g)' : [],
        'Wrist Roll (deg)' : [],
        'Wrist Pitch (deg)' : [],
        'Wrist Yaw (deg)' : [],
        'Arm Gyroscope X (deg/s)' : [],
        'Arm Gyroscope Y (deg/s)' : [],
        'Arm Gyroscope Z (deg/s)' : [],
        'Arm Accelerometer X (g)' : [],
        'Arm Accelerometer Y (g)' : [],
        'Arm Accelerometer Z (g)' : [],
        'Arm Roll (deg)' : [],
        'Arm Pitch (deg)' : [],
        'Arm Yaw (deg)' : [],
    }

    for i in range(min(len(df_arm), len(df_wrist))):
        for key, val_arm in df_arm.loc[i].to_dict().items():
            val_wrist = df_wrist.loc[i].to_dict()[key]
            if key == 'Timestamp (ms)':
                all_data[key].append(val_wrist)
            else:
                all_data[f'Wrist {key}'].append(val_wrist)
                all_data[f'Arm {key}'].append(val_arm)
    
    return pd.DataFrame(all_data)

def get_all_baseline_means(folder_path):
    all_data = {
        'Wrist Gyroscope X (deg/s)' : [],
        'Wrist Gyroscope Y (deg/s)' : [],
        'Wrist Gyroscope Z (deg/s)' : [],
        'Wrist Accelerometer X (g)' : [],
        'Wrist Accelerometer Y (g)' : [],
        'Wrist Accelerometer Z (g)' : [],
        'Wrist Roll (deg)' : [],
        'Wrist Pitch (deg)' : [],
        'Wrist Yaw (deg)' : [],
        'Arm Gyroscope X (deg/s)' : [],
        'Arm Gyroscope Y (deg/s)' : [],
        'Arm Gyroscope Z (deg/s)' : [],
        'Arm Accelerometer X (g)' : [],
        'Arm Accelerometer Y (g)' : [],
        'Arm Accelerometer Z (g)' : [],
        'Arm Roll (deg)' : [],
        'Arm Pitch (deg)' : [],
        'Arm Yaw (deg)' : [],
        'Difference Roll (deg)' : [],
        'Difference Pitch (deg)' : [],
        'Difference Yaw (deg)' : [],
    }
    euler_df_wrist = get_euler_df(folder_path, 'Baseline', 'wrist')
    euler_df_arm = get_euler_df(folder_path, 'Baseline', 'arm')
    inertial_df_wrist = get_inertial_df(folder_path, 'Baseline', 'wrist')
    inertial_df_arm = get_inertial_df(folder_path, 'Baseline', 'arm')
    for key, val in euler_df_wrist.mean().to_dict().items():
        if key != 'Timestamp (ms)':
            all_data[f'Wrist {key}'].append(val)
    for key, val in euler_df_arm.mean().to_dict().items():
        if key != 'Timestamp (ms)':
            all_data[f'Arm {key}'].append(val)
    for key, val in inertial_df_wrist.mean().to_dict().items():
        if key != 'Timestamp (ms)':
            all_data[f'Wrist {key}'].append(val)
    for key, val in inertial_df_arm.mean().to_dict().items():
        if key != 'Timestamp (ms)':
            all_data[f'Arm {key}'].append(val)
    for key, val in get_mean_baseline(folder_path).items():
        if key != 'Timestamp (ms)':
            all_data[f'Difference {key}'].append(val)
    return pd.DataFrame(all_data)

def extract_features(data):
    features = []
    features.append(np.mean(data))                                      # mean
    features.append(np.std(data))                                       # standard deviation
    features.append(np.max(data) - np.min(data))                        # range
    features.append(np.sqrt(np.mean(data**2)))                          # root mean square
    features.append(np.corrcoef(data[:-1], data[1:])[0, 1])             # lag 1 autocorrelation

    features.append(np.skew(data))
    features.append(np.kurtosis(data))

    # power spectral density
    nperseg = min(256, len(data))
    f, Pxx = welch(data, nperseg=nperseg)
    features.append(np.sum(Pxx))                                        # total power

    return features