# main.py

from models import Timetable, Group, Subject, Lecturer, Room
from utils import load_data, schedule_to_csv, save_schedule_to_excel
from genetic_algorithm import GeneticAlgorithm

def main() -> None:
    # Load data from CSV files
    groups, subjects_list, lecturers, rooms = load_data()

    # Parameters for the genetic algorithm
    population_size = 50
    generations = 1000
    mutation_rate = 0.4
    crossover_pairs = 10

    # Create an instance of the genetic algorithm
    ga = GeneticAlgorithm(
        groups=groups,
        subjects=subjects_list,
        lecturers=lecturers,
        rooms=rooms,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        crossover_pairs=crossover_pairs
    )

    # Generate the initial population
    ga.create_population()

    # Run the genetic algorithm
    best_timetable = ga.run()

    # Save the schedule to Excel files
    save_schedule_to_excel(best_timetable, output_folder="schedules")
    print("Schedules saved to Excel files in the 'schedules' folder.")

    # Also, print the fitness of the best schedule
    best_fitness = ga.calculate_individual_fitness(best_timetable)
    print(f"Best schedule fitness: {best_fitness}")

if __name__ == "__main__":
    main()
