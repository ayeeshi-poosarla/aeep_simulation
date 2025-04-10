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
    force_threshold = 10.0 # bennett pls fix
  
    x_min = 1
    x_max = 1
    y_min = 1
    y_max = 1
    z_min = 1
    z_max = 1
  
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
