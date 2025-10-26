import pandas as pd
import matplotlib.pyplot as plt

cols = ['timestamp'] + [f'force_{i+1}' for i in range(15)]
df = pd.read_csv('master/force_sensing/EA6/force_log.csv', names=cols, skiprows=1)

# Convert timestamp to float
df['timestamp'] = df['timestamp'].astype(float)

# Convert timestamp to delta t (time elapsed from start in seconds)
df['delta_t'] = df['timestamp'] - df['timestamp'].iloc[0]

# Prepare subplots (grid with 3 columns)
num_sensors = 15
fig, axs = plt.subplots(nrows=5, ncols=3, figsize=(18, 12), sharex=True)
axs = axs.flatten()  # To simplify iteration

for i in range(num_sensors):
    sensor_col = f'force_{i+1}'
    
    # Calculate statistics
    min_val = df[sensor_col].min()
    max_val = df[sensor_col].max()
    avg_val = df[sensor_col].mean()
    
    # Plot the data
    axs[i].plot(df['delta_t'], df[sensor_col])
    axs[i].set_title(f'{sensor_col}')
    axs[i].set_xlabel('Time (s)')
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

plt.tight_layout()
plt.show()