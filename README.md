# Real-Time System Structure
Under Systems folder:

## `main.py`
- Entry point of the system. Run this script to start the system.
- Automatically creates a new folder named `individual_xx` under `Data/Participants`, where all files saved during the experiment will be stored.

## `SetupPage.py`
- The first page of the system, responsible for setting up the xIMU connections.
- References `ConnectionSetup.py`, which contains wrapper classes for xIMU API calls to set up the connections.
- **xIMU Devices Used**:
  - **Arm IMU**
    - **Serial Number**: `655782F7`
    - **Device Name**: `violet_IMU`
  - **Wrist IMU**
    - **Serial Number**: `65577B49`
    - **Device Name**: `green_IMU`

## `BasicInformationPage.py`
- The second page of the system, used to record demographic information about the individual.
- Saves the data as `basic_info.csv`.

## `TestAndCollectPage.py`
- The third page of the system, which displays the model prediction and allows for Borg logging.
- References `DataStreamer.py`, which computes peaks, extracts features from time windows, and runs model inference.
- Saves the RNN model predictions as `rnn_predictions.npy`
- Saves the IMU data as `imu_data.csv`
- Saves the indices of the segment intervals as `repetitions.csv`
- Saves the Borg logs as `borg.csv`
