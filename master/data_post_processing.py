import pandas as pd

# Example structure for input data
# These would typically come from sensors or logs
trainee_data = {
    'time_sec': 520,
    'enucleated_mass_g': 18.5,
    'force_violations': 7,
    'path_length_cm': 153.2,
    'idle_time_percent': 12.4
}

expert_data = {
    'time_sec': 480,
    'enucleated_mass_g': 20.0,
    'force_violations': 2,
    'path_length_cm': 140.0,
    'idle_time_percent': 5.0
}

def calculate_percent_score(trainee_val, expert_val, inverse=False):
    """
    Computes a percent score comparing trainee to expert.
    If inverse=True, lower trainee values are better.
    """
    if inverse:
        return max(0, min(100, 100 * expert_val / trainee_val))
    else:
        return max(0, min(100, 100 * trainee_val / expert_val))

def process_dashboard_metrics(trainee, expert):
    scores = {}
    scores['Time (sec)'] = trainee['time_sec']
    scores['Time Score (%)'] = calculate_percent_score(trainee['time_sec'], expert['time_sec'], inverse=True)

    scores['Enucleated Mass (g)'] = trainee['enucleated_mass_g']
    scores['Enucleated Mass Score (%)'] = calculate_percent_score(trainee['enucleated_mass_g'], expert['enucleated_mass_g'])

    scores['Force Violations'] = trainee['force_violations']
    scores['Force Violations Score (%)'] = calculate_percent_score(trainee['force_violations'], expert['force_violations'], inverse=True)

    scores['Path Length (cm)'] = trainee['path_length_cm']
    scores['Path Length Score (%)'] = calculate_percent_score(trainee['path_length_cm'], expert['path_length_cm'], inverse=True)

    scores['Idle Time (%)'] = trainee['idle_time_percent']
    scores['Idle Time Score (%)'] = calculate_percent_score(trainee['idle_time_percent'], expert['idle_time_percent'], inverse=True)

    # Weighted average for overall score (adjust weights as needed)
    weights = {
        'Time': 0.2,
        'Mass': 0.25,
        'Force': 0.15,
        'Path': 0.2,
        'Idle': 0.2
    }

    overall = (
        scores['Time Score (%)'] * weights['Time'] +
        scores['Enucleated Mass Score (%)'] * weights['Mass'] +
        scores['Force Violations Score (%)'] * weights['Force'] +
        scores['Path Length Score (%)'] * weights['Path'] +
        scores['Idle Time Score (%)'] * weights['Idle']
    )
    scores['Overall Score (%)'] = round(overall, 2)

    return pd.DataFrame([scores])

# Example usage
df_dashboard = process_dashboard_metrics(trainee_data, expert_data)
print(df_dashboard)
