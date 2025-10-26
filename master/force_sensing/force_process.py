import pandas as pd
import matplotlib.pyplot as plt

cols = ['timestamp'] + [f'force_{i+1}' for i in range(14)]
df = pd.read_csv('master/force_sensing/EA5/force_log.csv', names=cols, skiprows=1)

df['timestamp'] = df['timestamp'].astype(float)

df['total_force'] = df[[f'force_{i+1}' for i in range(14)]].sum(axis=1)

calibration_threshold = 50.0
calibration_end_idx = df[df['total_force'] > calibration_threshold].index
if len(calibration_end_idx) > 0:
    start_idx = calibration_end_idx[0]
else:
    start_idx = 0  

df = df.iloc[start_idx:].copy()

df['delta_t'] = df['timestamp'] - df['timestamp'].iloc[0]

num_sensors = 14
fig, axs = plt.subplots(nrows=5, ncols=3, figsize=(18, 12), sharex=True)
axs = axs.flatten()  # To simplify iteration

for i in range(num_sensors):
    sensor_col = f'force_{i+1}'
    
    # Calculate statistics (only for non-zero values)
    nonzero_values = df[sensor_col][df[sensor_col] != 0]
    if len(nonzero_values) > 0:
        min_val = nonzero_values.min()
        max_val = nonzero_values.max()
        avg_val = nonzero_values.mean()
    else:
        min_val = 0
        max_val = df[sensor_col].max()
        avg_val = df[sensor_col].mean()
    
    # Plot the data
    axs[i].plot(df['delta_t'], df[sensor_col])
    axs[i].set_title(f'{sensor_col}')
    axs[i].set_ylabel('Force Reading')
    
    # Add statistics as text on the plot
    stats_text = f'Min: {min_val:.2f}\nMax: {max_val:.2f}\nAvg: {avg_val:.2f}'
    axs[i].text(0.02, 0.98, stats_text, 
                transform=axs[i].transAxes, 
                fontsize=9, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Remove extra subplots
for j in range(num_sensors, len(axs)):
    fig.delaxes(axs[j])

fig.text(0.5, 0.02, 'Time (s)', ha='center', fontsize=12)

plt.tight_layout()
plt.subplots_adjust(bottom=0.05)  # Make room for the x-axis label
plt.show()