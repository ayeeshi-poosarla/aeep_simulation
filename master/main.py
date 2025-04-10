# main.py
import dof9_filter.py
import dof9_parser.py
import force_analysis.py
import force_reader.py
import imu_reader.py

def main():
    stl_file = "bph_mold_combined.stl" # your path
    df = []
    time_above_pressure_thresh = 0
    time_threshold = 3.0
    force_threshold = 10.0
  
    x_min = -75.485
    x_max = 75.485
    y_min = -82.4505
    y_max = 82.4505
    z_min = -63.0095
    z_max = 63.0095
  
    while (
      x_min <= x <= x_max and
      y_min <= y <= y_max and
      z_min <= z <= z_max
    ):
        imu_outputs = IMU_reader()
        bend_values = force_reader()
        coordinates = madgwick(imu_outputs)

        
        pressure = force_analysis(bend_values)
      
        projection_plane(coordinates) # update point on minimap

        # force thresholding

        if pressure > force_threshold:
            time_above_pressure_thresh += dt
        else:
            time_above_pressure_thresh = 0

        if time_above_pressure_thresh > time_threshold:
            change_color()

        N, S, E, W = force_reader()
        data = {dt, x, y, z, N, S, E, W}
        df.append(data)


if __name__ == "__main__":
    main()
