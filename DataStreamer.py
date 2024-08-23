import pandas as pd
from collections import defaultdict
import math
import numpy as np
import lightgbm as lgb
from scipy.signal import welch, find_peaks
from scipy.stats import skew, kurtosis
from scipy.fft import fft
import joblib
from datetime import datetime
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import load_model

class DataStreamer():
    def __init__(self, wrist_connection, arm_connection):
        model_folder = '/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/models'
        self.rnn_model = load_model(f'{model_folder}/rnn.keras')

        self.rnn_indices = [12, 18, 221, 224, 156, 162, 35, 36, 67, 75, 100, 108, 205, 206, 210, 215, 218, 233, 237]

        self.scaler = joblib.load(f'{model_folder}/scaler_rnn.pkl')

        # self.lgbm_model = lgb.Booster(model_file='/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/models/lgbm.txt')
        # self.lgbm_indices = [149, 8, 21, 135, 38, 103, 145, 130, 114, 116, 119, 134, 122, 11, 63]

        # self.lr_model = joblib.load('/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/models/lr.pkl')
        # self.lr_indices = [100, 108, 80, 53, 135, 9, 49, 151, 21, 116, 132, 152, 149, 111, 138, 12, 38, 70, 97, 137]

        # self.svr_model = joblib.load('/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/models/svr.pkl')
        # self.svr_indices = [103, 149, 92, 108, 145, 10, 97, 138, 12, 21, 8, 36, 111, 148, 85, 113, 9, 86, 114, 139, 141, 40, 135, 37, 55, 151, 22]

        self.wrist_connection = wrist_connection
        self.arm_connection = arm_connection

        self.timestamps = []
        self.data = defaultdict(lambda: {
            'Wrist Gyroscope X (deg/s)': None,
            'Wrist Gyroscope Y (deg/s)': None,
            'Wrist Gyroscope Z (deg/s)': None,
            'Wrist Accelerometer X (g)': None,
            'Wrist Accelerometer Y (g)': None,
            'Wrist Accelerometer Z (g)': None,
            'Wrist Roll (deg)': None,
            'Wrist Pitch (deg)': None,
            'Wrist Yaw (deg)': None,
            'Arm Gyroscope X (deg/s)': None,
            'Arm Gyroscope Y (deg/s)': None,
            'Arm Gyroscope Z (deg/s)': None,
            'Arm Accelerometer X (g)': None,
            'Arm Accelerometer Y (g)': None,
            'Arm Accelerometer Z (g)': None,
            'Arm Roll (deg)': None,
            'Arm Pitch (deg)': None,
            'Arm Yaw (deg)': None,
            'Wrist Gyroscope Magnitude (deg/s)': None,
            'Wrist Accelerometer Magnitude (g)': None,
            'Arm Gyroscope Magnitude (deg/s)': None,
            'Arm Accelerometer Magnitude (g)': None,
        })

        self.euler_wrist_i = 0
        self.euler_arm_i = 0
        self.inertial_wrist_i = 0
        self.inertial_arm_i = 0

        self.roll_data = []
        self.pitch_data = []
        self.yaw_data = []

        self.intervals = []
        self.peak_pitch_min = 60
        self.peaks = []

        self.fatigue = 'None'
        self.all_fatigue = []

        self.normalization_matrix = None
        self.data_segments = []
        
        self.start()

    def start(self):
        self.wrist_connection.add_euler_angles_callback(self.euler_callback_wrist)
        self.arm_connection.add_euler_angles_callback(self.euler_callback_arm)
        self.wrist_connection.add_inertial_callback(self.inertial_callback_wrist)
        self.arm_connection.add_inertial_callback(self.inertial_callback_arm)
        print('xIMU successfully started streaming')

    def trim(self, cutoff, target_data):
        if cutoff < len(target_data):
            return target_data[:cutoff]
        if cutoff > len(target_data):
            return self.padded(target_data, cutoff)
        return target_data

    def padded(self, target_data, cutoff):
        padded_data = np.full(cutoff, np.nan)
        padded_data[:len(target_data)] = target_data
        return padded_data
    
    def end(self, folder_path):
        try:
            data_df = pd.DataFrame(self.data)
            data_df = data_df.transpose()
            cutoff = min(len(self.timestamps), len(data_df.index))
            data_df = data_df.iloc[:cutoff]

            data_df['Difference Roll (deg)'] = self.trim(cutoff, self.roll_data)
            data_df['Difference Pitch (deg)'] = self.trim(cutoff, self.pitch_data)
            data_df['Difference Yaw (deg)'] = self.trim(cutoff, self.yaw_data)
            data_df.index = self.trim(cutoff, self.timestamps)

            min_time = data_df.index.min()
            data_df.index = ((data_df.index - min_time).total_seconds() * 1000).rename('Timestamp (ms)')
            data_df.dropna(inplace=True)
            data_df.to_csv(f"{folder_path}/imu_data.csv", index=True)
                        
        except:
            print('ERROR')
            data_df = pd.DataFrame(self.data)
            data_df = data_df.transpose()
            cutoff = min(len(self.timestamps), len(data_df.index))
            data_df = data_df.iloc[:cutoff]

            data_df['Difference Roll (deg)'] = self.trim(cutoff, self.roll_data)
            data_df['Difference Pitch (deg)'] = self.trim(cutoff, self.pitch_data)
            data_df['Difference Yaw (deg)'] = self.trim(cutoff, self.yaw_data)
            data_df.index = self.trim(cutoff, self.timestamps)
            data_df.to_csv(f"{folder_path}/imu_data.csv", index=True)

        repetitions_df = pd.DataFrame(self.intervals, columns=['start (index)', 'end (index)'])
        repetitions_df.to_csv(f"{folder_path}/repetitions.csv", index=False)
        print(len(self.data_segments))
        print('IMU data has been saved')

        np.save(f'{folder_path}/rnn_predictions.npy', np.array(self.all_fatigue))

    
    def _update_data(self, key, column, value):
        self.data[key][column] = value

    def _update_diff(self, key, type):
        if type == 'pitch':
            self.pitch_data.append(self.data[key]['Arm Pitch (deg)'] - self.data[key]['Wrist Pitch (deg)'])
            self._compute_peaks()
        if type == 'roll':
            self.roll_data.append(self.data[key]['Arm Roll (deg)'] - self.data[key]['Wrist Roll (deg)'])
        if type == 'yaw':
            self.yaw_data.append(self.data[key]['Arm Yaw (deg)'] - self.data[key]['Wrist Yaw (deg)'])
        
    def _calculate_magnitude(self, x, y, z):
        return math.sqrt(x**2 + y**2 + z**2)

    def _compute_peaks(self):
        n = len(self.pitch_data)
        if n <= 2:
            return
        if self.pitch_data[-2] > self.pitch_data[-3] and self.pitch_data[-2] > self.pitch_data[-1]:
            if self.pitch_data[-2] > self.peak_pitch_min:
                current_peak = n - 2
                if len(self.peaks) > 0 and self.pitch_data[(self.peaks[-1] + current_peak) // 2] > self.peak_pitch_min:
                    current_peak = (self.peaks[-1] + current_peak) // 2
                    self.peaks[-1] = current_peak
                else:
                    self.peaks.append(current_peak)
                    if len(self.peaks) >= 3:
                        start_point = self.peaks[-3]
                        end_point = self.peaks[-1]

                        self.intervals.append((start_point, end_point))

                        remaining_data = np.array([list(self.data[key].values()) for key in range(start_point, end_point+1)])
                        roll_data = np.array([self.roll_data[key] for key in range(start_point, end_point+1)]).reshape(-1, 1)
                        pitch_data = np.array([self.pitch_data[key] for key in range(start_point, end_point+1)]).reshape(-1, 1)
                        yaw_data = np.array([self.yaw_data[key] for key in range(start_point, end_point+1)]).reshape(-1, 1)

                        data_segment = self.smoothen(np.hstack((remaining_data, roll_data, pitch_data, yaw_data)))
                        feature_matrix = self.extract_feature_matrix(data_segment)
                        if len(self.peaks) == 3:
                            self.normalization_matrix = np.where(feature_matrix == 0, 1e-8, feature_matrix)
                        feature_matrix = feature_matrix / self.normalization_matrix
                        feature_matrix = feature_matrix.reshape(1, -1)
                        feature_matrix_scaled = self.scaler.transform(feature_matrix)
                        self.data_segments.append(feature_matrix_scaled.flatten())
                        prediction = self.predict_rnn(self.rnn_model)
                        self.all_fatigue.append(prediction)
                        label = self.get_label(prediction)
                        self.fatigue = f'{label} ({prediction:.1f})'

    def get_label(self, value):
        if value < 3:
            return 'Low'
        if value >= 5:
            return 'High'
        return 'Moderate'
    
    def predict_rnn(self, model):
        if len(self.data_segments) > 0:
            X_test = np.stack(self.data_segments)
            X_test = X_test[:, self.rnn_indices]
            X_test = np.expand_dims(X_test, axis=0)
            prediction = np.squeeze(model.predict(X_test, verbose=0))
            if len(prediction.shape) == 0:
                return prediction
            else:
                return prediction[-1]

    def smoothen(self, data_segment, window_size_ms = 100):
        # 100 ms equates to sliding window of 5 samples
        # data segment is a 2d numpy array
        df = pd.DataFrame(data_segment)
        sampling_interval_ms = 20
        window_size_samples = int(window_size_ms / sampling_interval_ms)
        smoothened_df = df.rolling(window=window_size_samples, min_periods=1).mean()
        return smoothened_df.values

    def extract_feature_matrix(self, data_segment):
        feature_matrix = []
        for col_index in range(data_segment.shape[1]):
            feature_matrix.append(self.extract_features(data_segment[:, col_index]))
        return np.array(feature_matrix).flatten()

    def extract_features(self, data):
        features = []
        features.append(np.mean(data))                           # mean
        features.append(np.std(data))                            # standard deviation
        features.append(skew(data))                              # skewness
        features.append(kurtosis(data))                          # kurtosis
        features.append(np.max(data) - np.min(data))             # range
        features.append(np.max(data))                            # maximum
        features.append(np.min(data))                            # minimum
        features.append(np.sqrt(np.mean(data**2)))               # root mean square
        features.append(np.corrcoef(data[:-1], data[1:])[0, 1])  # lag 1 autocorrelation

        # power spectral density
        nperseg = min(256, len(data))
        f, Pxx = welch(data, nperseg=nperseg)
        features.append(np.sum(Pxx))                             # total power

        # fast fourier transform
        fft_values = np.abs(fft(data))
        fft_freqs = np.fft.fftfreq(len(fft_values))
        peaks, _ = find_peaks(fft_values)                        # dominant frequency
        features.append(fft_freqs[peaks[0]] if peaks.size > 0 else 0)      
        return features
    
    def euler_callback_wrist(self, message):
        key = self.euler_wrist_i
        self._update_data(key, 'Wrist Roll (deg)', message.roll)
        self._update_data(key, 'Wrist Pitch (deg)', message.pitch)
        self._update_data(key, 'Wrist Yaw (deg)', message.yaw)

        if self.data[key]['Arm Pitch (deg)'] is not None:
            self._update_diff(key, type='pitch')

        if self.data[key]['Arm Roll (deg)'] is not None:
            self._update_diff(key, type='roll')

        if self.data[key]['Arm Yaw (deg)'] is not None:
            self._update_diff(key, type='yaw')

        self.euler_wrist_i += 1
        self.timestamps.append(datetime.now())

    def euler_callback_arm(self, message):
        key = self.euler_arm_i
        self._update_data(key, 'Arm Roll (deg)', message.roll)
        self._update_data(key, 'Arm Pitch (deg)', message.pitch)
        self._update_data(key, 'Arm Yaw (deg)', message.yaw)
        
        if self.data[key]['Wrist Pitch (deg)'] is not None:
            self._update_diff(key, type='pitch')

        if self.data[key]['Wrist Roll (deg)'] is not None:
            self._update_diff(key, type='roll')

        if self.data[key]['Wrist Yaw (deg)'] is not None:
            self._update_diff(key, type='yaw')

        self.euler_arm_i += 1

    def inertial_callback_wrist(self, message):
        key = self.inertial_wrist_i
        self._update_data(key, 'Wrist Gyroscope X (deg/s)', message.gyroscope_x)
        self._update_data(key, 'Wrist Gyroscope Y (deg/s)', message.gyroscope_y)
        self._update_data(key, 'Wrist Gyroscope Z (deg/s)', message.gyroscope_z)
        self._update_data(key, 'Wrist Accelerometer X (g)', message.accelerometer_x)
        self._update_data(key, 'Wrist Accelerometer Y (g)', message.accelerometer_y)
        self._update_data(key, 'Wrist Accelerometer Z (g)', message.accelerometer_z)

        gyro_magnitude = self._calculate_magnitude(message.gyroscope_x, message.gyroscope_y, message.gyroscope_z)
        accel_magnitude = self._calculate_magnitude(message.accelerometer_x, message.accelerometer_y, message.accelerometer_z)

        self._update_data(key, 'Wrist Gyroscope Magnitude (deg/s)', gyro_magnitude)
        self._update_data(key, 'Wrist Accelerometer Magnitude (g)', accel_magnitude)

        self.inertial_wrist_i += 1

    def inertial_callback_arm(self, message):
        key = self.inertial_arm_i
        self._update_data(key, 'Arm Gyroscope X (deg/s)', message.gyroscope_x)
        self._update_data(key, 'Arm Gyroscope Y (deg/s)', message.gyroscope_y)
        self._update_data(key, 'Arm Gyroscope Z (deg/s)', message.gyroscope_z)
        self._update_data(key, 'Arm Accelerometer X (g)', message.accelerometer_x)
        self._update_data(key, 'Arm Accelerometer Y (g)', message.accelerometer_y)
        self._update_data(key, 'Arm Accelerometer Z (g)', message.accelerometer_z)

        gyro_magnitude = self._calculate_magnitude(message.gyroscope_x, message.gyroscope_y, message.gyroscope_z)
        accel_magnitude = self._calculate_magnitude(message.accelerometer_x, message.accelerometer_y, message.accelerometer_z)

        self._update_data(key, 'Arm Gyroscope Magnitude (deg/s)', gyro_magnitude)
        self._update_data(key, 'Arm Accelerometer Magnitude (g)', accel_magnitude)

        self.inertial_arm_i += 1
