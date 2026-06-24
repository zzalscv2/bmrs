import pandas as pd
import matplotlib.pyplot as plt

def parse_duration(duration_str):
    """Converts a duration string 'H:MM' into total hours as a float."""
    if pd.isna(duration_str) or not str(duration_str).strip():
        return 0.0
    try:
        parts = str(duration_str).split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours + (minutes / 60.0)
    except Exception:
        return 0.0

def main():
    # 1. Read the data from eva-data.json
    print("Loading JSON data...")
    df = pd.read_json('eva-data.json')

    # 2. Clean the data
    print("Cleaning data...")
    # Convert dates to datetime objects, invalid formats become NaT (Not a Time)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop rows that don't have a valid date
    df = df.dropna(subset=['date'])
    
    # Parse durations into a numeric 'duration_hours' column
    df['duration_hours'] = df['duration'].apply(parse_duration)
    
    # Clean up the crew column: remove trailing semicolons and split into a list
    # e.g., "Neil Armstrong;Buzz Aldrin;" -> ['Neil Armstrong', 'Buzz Aldrin']
    df['crew_list'] = df['crew'].fillna('').apply(
        lambda x: [name.strip() for name in x.strip('; ').split(';') if name.strip()]
    )

    # 3 & 4 & 5. Write a cleaned CSV file
    print("Exporting cleaned data to eva-data.csv...")
    # Drop the temporary list column for a cleaner CSV output
    cleaned_df = df.drop(columns=['crew_list'])
    cleaned_df.to_csv('eva-data.csv', index=False)

    # 6. Calculate summary table for total EVA per astronaut
    print("Calculating astronaut summary...")
    # Explode the dataframe so each astronaut gets their own row for the duration of the EVA
    exploded_df = df.explode('crew_list')
    
    # Group by the astronaut's name and sum their EVA hours
    astronaut_summary = exploded_df.groupby('crew_list')['duration_hours'].sum().reset_index()
    astronaut_summary.columns = ['Astronaut', 'Total_EVA_Hours']
    astronaut_summary = astronaut_summary.sort_values(by='Total_EVA_Hours', ascending=False)

    # 7. Save summary duration data by each astronaut to CSV file
    print("Exporting astronaut summary to astronaut_summary.csv...")
    astronaut_summary.to_csv('astronaut_summary.csv', index=False)

    # 8. Sort data by date
    print("Sorting data by date...")
    df = df.sort_values(by='date')

    # 9. Calculate cumulative EVA time by date
    print("Calculating cumulative EVA time...")
    df['cumulative_hours'] = df['duration_hours'].cumsum()

    # 10 & 11 & 12. Plot cumulative time, save to root, and open for viewing
    print("Generating plot...")
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['cumulative_hours'], marker='o', linestyle='-', markersize=3, color='b')
    
    # Formatting the plot
    plt.title('Cumulative Spacewalk (EVA) Time Over the Years', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Time (Hours)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to the root directory
    plot_filename = 'cumulative_eva_graph.png'
    plt.savefig(plot_filename)
    print(f"Plot saved successfully as '{plot_filename}'.")

    # Open the plot for viewing
    print("Opening plot...")
    plt.show()

if __name__ == "__main__":
    main()