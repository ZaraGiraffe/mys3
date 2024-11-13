# main.py

from models import Timetable, Group, Subject, Lecturer, Room
from utils import load_data, schedule_to_csv, save_schedule_to_excel
from genetic_algorithm import GeneticAlgorithm

def main() -> None:
    groups, subjects_list, lecturers, rooms = load_data()

    population_size = 50
    generations = 1000
    mutation_rate = 0.4
    crossover_pairs = 10

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

    ga.create_population()

    best_timetable = ga.run()

    save_schedule_to_excel(best_timetable, output_folder="schedules")
    print("Schedules saved to Excel files in the 'schedules' folder.")

    best_fitness = ga.calculate_individual_fitness(best_timetable)
    print(f"Best schedule fitness: {best_fitness}")

if __name__ == "__main__":
    main()
