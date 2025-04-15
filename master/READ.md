# Simulation System – Real Time Position Feedback

This simulation system is written in Python. It uses `main.py` as the primary entry point and imports code from other modules in the same folder to provide real-time position feedback. Although Python is an interpreted language (and does not require traditional compilation), follow these instructions to set up and run the simulation.

## Prerequisites

1. **Python Installation**
   - Ensure you have Python 3 installed.
   - Verify by running:
     ```bash
     python3 --version
     ```
   - If not installed, download it from [python.org](https://www.python.org/downloads/).

2. **Virtual Environment**
   - To create an isolated Python environment, run:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     - **macOS/Linux:**
       ```bash
       source venv/bin/activate
       ```
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```

3. **Dependencies**
   - If your project requires external packages, list them in a `requirements.txt` file.
   - Install dependencies with:
     ```bash
     pip install -r requirements.txt
     ```

## Project Structure

/simulation-system
   ├── coordinates.txt    # Data file for coordinate information
   ├── dof9_filter.py     # Code for filtering data from a 9-DOF sensor
   ├── dof9_parser.py     # Code for parsing data from a 9-DOF sensor
   ├── force_analysis.py  # Code analyzing force data
   ├── force_reader.py    # Code handling force data reading
   ├── imu_reader.py      # Code for reading IMU (Inertial Measurement Unit) data
   └── main.py            # Main entry point for the simulation

## Running the Simulation Model

To run the simulation, follow these steps:

1. **Navigate to the Project Directory**
- Open your terminal and change to the project directory:
    ```cd /path/to/simulation-system```

2. **(Optional) Activate the Virtual Environment**
- On macOS/Linux:
    ```source venv/bin/activate```
- On Windows:
    ```venv\Scripts\activate```

3. **Run the Main Script**
- Launch the simulation by running:
    ```python3 main.py```