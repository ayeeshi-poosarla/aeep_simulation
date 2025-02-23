import re
import numpy as np

class IMUPositionEstimator:
    def __init__(self, dt=0.01):
        """Initialize with default time step and store previous values."""
        self.dt = dt
        self.prev_velocity = np.array([0.0, 0.0, 0.0])
        self.prev_position = np.array([0.0, 0.0, 0.0])
        self.prev_accel = np.array([0.0, 0.0, 0.0])
        self.pattern = re.compile(r"Ax=(-?\d+\.\d+).+?Ay=(-?\d+\.\d+).+?Az=(-?\d+\.\d+)")

    def update_position(self, line):
        """Process a single line of IMU data and return updated position."""
        match = self.pattern.search(line)
        if not match:
            return self.prev_position  # Return last known position if no match

        # Parse acceleration values
        accel = np.array(list(map(float, match.groups())))

        # Integrate acceleration to estimate velocity
        velocity = self.prev_velocity + (self.prev_accel + accel) / 2 * self.dt  # Trapezoidal integration

        # Integrate velocity to estimate position
        position = self.prev_position + (self.prev_velocity + velocity) / 2 * self.dt  # Trapezoidal integration

        # Update previous values
        self.prev_accel = accel
        self.prev_velocity = velocity
        self.prev_position = position

        return position