import pandas as pd
import matplotlib.pyplot as plt

cols = ['timestamp'] + [f'force_{i+1}' for i in range(15)]
df = pd.read_csv('/Users/gracenoh/Downloads/force_log (1).csv', names=cols, header=None)

# Prepare subplots (let's put in a grid with 3 columns)
num_sensors = 15
fig, axs = plt.subplots(nrows=5, ncols=3, figsize=(18, 12), sharex=True)
axs = axs.flatten()  # To simplify iteration

for i in range(num_sensors):
    sensor_col = f'force_{i+1}'
    axs[i].plot(df['timestamp'], df[sensor_col])
    axs[i].set_title(sensor_col)
    axs[i].set_xlabel('Timestamp')
    axs[i].set_ylabel('Force Reading')


for j in range(num_sensors, len(axs)):
    fig.delaxes(axs[j])

plt.tight_layout()
plt.show()
