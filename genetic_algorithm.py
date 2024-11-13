# genetic_algorithm.py

from models import Timetable, Group, Subject, Lecturer, Room
from typing import List, Tuple, Dict
import random
from utils import check_constraints, TIME_SLOTS

class GeneticAlgorithm:
    def __init__(
        self,
        groups: List[Group],
        subjects: List[Subject],
        lecturers: List[Lecturer],
        rooms: List[Room],
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_pairs: int = 10
    ):
        self.groups = groups
        self.subjects = subjects
        self.subjects_dict = {subject.name: subject for subject in subjects}
        self.lecturers = lecturers
        self.rooms = rooms
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_pairs = crossover_pairs  # Parameter for number of crossover pairs
        self.population: List[Timetable] = []
        self.fitness_scores: List[float] = []

    def create_population(self):
        for _ in range(self.population_size):
            timetable = self.generate_valid_schedule()
            self.population.append(timetable)
        self.calculate_fitness()

    def generate_valid_schedule(self) -> Timetable:
        """
        Generates a timetable that satisfies the hard constraints.
        Assigns lectures and practices separately, ensuring lecturer qualifications.
        """
        timetable = Timetable()
        lecturer_schedule = {}
        room_schedule = {}
        group_schedule = {}

        for group in self.groups:
            for subject_name in group.subjects:
                subject = self.subjects_dict[subject_name]
                for session_type in ['Lecture', 'Practice']:
                    if session_type == 'Lecture' and subject.lecture_hours > 0:
                        total_possible_sessions = int(subject.lecture_hours / 5)
                    elif session_type == 'Practice' and subject.practice_hours > 0:
                        total_possible_sessions = int(subject.practice_hours / 5)
                    else:
                        continue  # No hours required for this session type

                    sessions_to_assign = random.randint(1, total_possible_sessions)

                    for _ in range(sessions_to_assign):
                        random.shuffle(TIME_SLOTS)
                        for slot in TIME_SLOTS:
                            key = (group.group_id, slot)
                            if group_schedule.get((group.group_id, slot)):
                                continue

                            # Select suitable lecturers
                            suitable_lecturers = []
                            for lecturer in self.lecturers:
                                if subject.name in lecturer.subjects and session_type in lecturer.subjects[subject.name]:
                                    suitable_lecturers.append(lecturer)
                            random.shuffle(suitable_lecturers)

                            lecturer_found = False
                            for lecturer in suitable_lecturers:
                                if lecturer_schedule.get((lecturer.name, slot)):
                                    continue

                                suitable_rooms = [
                                    room for room in self.rooms if room.capacity >= group.size
                                ]
                                random.shuffle(suitable_rooms)
                                room_found = False
                                for room in suitable_rooms:
                                    if room_schedule.get((room.room_id, slot)):
                                        continue

                                    # Assign the session
                                    timetable.schedule[key] = (subject, lecturer, room, session_type)
                                    group_schedule[(group.group_id, slot)] = True
                                    lecturer_schedule[(lecturer.name, slot)] = True
                                    room_schedule[(room.room_id, slot)] = True
                                    room_found = True
                                    break
                                if room_found:
                                    lecturer_found = True
                                    break
                            if lecturer_found:
                                break
        return timetable

    def calculate_fitness(self):
        self.fitness_scores = []
        for timetable in self.population:
            fitness = self.calculate_individual_fitness(timetable)
            self.fitness_scores.append(fitness)

    def calculate_individual_fitness(self, timetable: Timetable) -> float:
        soft_violations = 0

        # Penalty for not covering required lecture and practice hours
        for group in self.groups:
            subject_sessions = {
                (subject_name, session_type): 0
                for subject_name in group.subjects
                for session_type in ['Lecture', 'Practice']
            }
            for (group_id, _), (subject, _, _, session_type) in timetable.schedule.items():
                if group_id == group.group_id:
                    subject_sessions[(subject.name, session_type)] += 1

            for subject_name in group.subjects:
                subject = self.subjects_dict[subject_name]
                for session_type in ['Lecture', 'Practice']:
                    if session_type == 'Lecture':
                        total_required_sessions = int(subject.lecture_hours / 5)
                    else:
                        total_required_sessions = int(subject.practice_hours / 5)
                    sessions_assigned = subject_sessions[(subject_name, session_type)]
                    difference = abs(sessions_assigned - total_required_sessions)
                    if difference > 0:
                        soft_violations += 10 * difference**4  # Increased penalty

        # Penalty for windows (gaps) in group schedules
        for group in self.groups:
            slots = [
                slot for (group_id, slot) in timetable.schedule.keys()
                if group_id == group.group_id
            ]
            soft_violations += 10 * self.count_windows(slots)**4  # Penalty per window

        # Penalty for windows in lecturer schedules
        lecturers = set(lecturer.name for _, lecturer, _, _ in timetable.schedule.values())
        for lecturer_name in lecturers:
            slots = [
                slot for ((_, slot), (_, lecturer, _, _)) in timetable.schedule.items()
                if lecturer.name == lecturer_name
            ]
            soft_violations += 2 * self.count_windows(slots)**2  # Penalty per window

        # Fitness score
        fitness = 1000 - soft_violations
        return fitness

    def count_windows(self, slots: List[Tuple[int, int]]) -> int:
        windows = 0
        schedule = {}
        for day, period in slots:
            schedule.setdefault(day, []).append(period)
        for periods in schedule.values():
            periods.sort()
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] > 1:
                    windows += periods[i+1] - periods[i] - 1
        return windows

    def run(self):
        for generation in range(self.generations):
            # Sort schedules by fitness
            self.calculate_fitness()
            schedules_with_fitness = list(zip(self.population, self.fitness_scores))
            schedules_with_fitness.sort(key=lambda x: x[1], reverse=True)
            best_schedules = [schedule for schedule, _ in schedules_with_fitness[:10]]

            # Select pairs for crossover
            remaining_schedules = [schedule for schedule, _ in schedules_with_fitness[10:]]
            new_schedules = []

            for _ in range(self.crossover_pairs):
                parents = random.sample(remaining_schedules, 2)
                child = self.crossover_days(parents[0], parents[1])
                if self.validate_schedule(child):
                    new_schedules.append(child)
                else:
                    # If invalid, generate a new valid schedule
                    child = self.generate_valid_schedule()
                    new_schedules.append(child)

            # Combine remaining schedules with new schedules
            combined_schedules = remaining_schedules + new_schedules

            # Mutate selected schedules
            schedules_to_mutate = random.sample(combined_schedules, 20)
            mutated_schedules = []
            for schedule in schedules_to_mutate:
                mutated_versions = self.mutate(schedule)  # Generate new schedules
                mutated_schedules.extend(mutated_versions)

            # Update combined_schedules with mutated schedules
            # Remove the original schedules that were mutated and add mutated versions
            combined_schedules = [
                schedule for schedule in combined_schedules if schedule not in schedules_to_mutate
            ] + mutated_schedules

            # Recalculate fitness for combined_schedules
            self.population = best_schedules + combined_schedules
            self.calculate_fitness()
            schedules_with_fitness = list(zip(self.population[10:], self.fitness_scores[10:]))
            schedules_with_fitness.sort(key=lambda x: x[1], reverse=True)
            # Select the best schedules to maintain population size
            selected_schedules = [schedule for schedule, _ in schedules_with_fitness[:(self.population_size - 10)]]

            # Update population for next generation
            self.population = best_schedules + selected_schedules

            # Calculate fitness for the new population
            self.calculate_fitness()

            # Output the best fitness
            best_fitness = max(self.fitness_scores)
            print(f"Generation {generation + 1}: Best Fitness = {best_fitness}")

        # Return the best timetable
        best_index = self.fitness_scores.index(max(self.fitness_scores))
        return self.population[best_index]

    def crossover_days(self, parent1: Timetable, parent2: Timetable) -> Timetable:
        """
        Performs crossover by dividing days into two sets and combining schedules.
        """
        days = list(set(slot[0] for (_, slot) in parent1.schedule.keys()))
        if not days:
            days = list(range(5))  # Assuming 5 days if parent1 has no schedule
        random.shuffle(days)
        split_point = len(days) // 2
        days_A = set(days[:split_point])
        days_B = set(days[split_point:])

        child = Timetable()

        for (group_id, slot), assignment in parent1.schedule.items():
            if slot[0] in days_A:
                child.schedule[(group_id, slot)] = assignment

        for (group_id, slot), assignment in parent2.schedule.items():
            if slot[0] in days_B:
                # Check for conflicts
                if (group_id, slot) not in child.schedule:
                    child.schedule[(group_id, slot)] = assignment

        return child

    def mutate(self, timetable: Timetable) -> List[Timetable]:
        """
        Generates multiple new schedules from the base schedule:
        - Schedule 0: base schedule (unchanged)
        - Schedule 1: base schedule with one lesson popped
        - Schedule 2: base schedule with one random lesson inserted (if valid)
        - Schedule 3: base schedule with a lesson popped from one group and a lesson added for another group (if valid)
        Returns a list of valid schedules.
        """
        new_schedules = []

        # Schedule 0: base schedule (unchanged)
        new_schedules.append(timetable)

        # Schedule 1: base schedule with one lesson popped
        timetable_popped = Timetable()
        timetable_popped.schedule = timetable.schedule.copy()
        # Select a random lesson to remove
        if timetable_popped.schedule:
            key_to_remove = random.choice(list(timetable_popped.schedule.keys()))
            timetable_popped.schedule.pop(key_to_remove)
            if self.validate_schedule(timetable_popped):
                new_schedules.append(timetable_popped)

        # Schedule 2: base schedule with one random lesson inserted (if valid)
        timetable_inserted = Timetable()
        timetable_inserted.schedule = timetable.schedule.copy()
        # Create a new lesson
        # Select a random group
        group = random.choice(self.groups)
        # Select a random subject from the group's subjects
        new_subject_name = random.choice(group.subjects)
        new_subject = self.subjects_dict[new_subject_name]
        # Select possible session types based on remaining hours
        possible_session_types = []
        if new_subject.lecture_hours > 0:
            possible_session_types.append('Lecture')
        if new_subject.practice_hours > 0:
            possible_session_types.append('Practice')
        if not possible_session_types:
            return new_schedules  # Cannot assign any sessions for this subject
        session_type = random.choice(possible_session_types)
        # Select a random time slot
        new_slot = random.choice(TIME_SLOTS)
        # Select a random lecturer who can teach the subject and session type
        suitable_lecturers = [
            lect for lect in self.lecturers
            if new_subject.name in lect.subjects and session_type in lect.subjects[new_subject.name]
        ]
        if suitable_lecturers:
            new_lecturer = random.choice(suitable_lecturers)
            # Select a random room that can accommodate the group
            suitable_rooms = [room for room in self.rooms if room.capacity >= group.size]
            if suitable_rooms:
                new_room = random.choice(suitable_rooms)
                # Check for conflicts
                if self.is_assignment_valid(timetable_inserted, group.group_id, new_slot, new_lecturer, new_room):
                    timetable_inserted.schedule[(group.group_id, new_slot)] = (new_subject, new_lecturer, new_room, session_type)
                    if self.validate_schedule(timetable_inserted):
                        new_schedules.append(timetable_inserted)

        # Schedule 3: base schedule with one lesson popped from one group and a lesson added for another group
        timetable_swap = Timetable()
        timetable_swap.schedule = timetable.schedule.copy()
        # Check if there are lessons to pop
        if timetable_swap.schedule:
            # Select a random group with lessons
            group_ids_with_lessons = set(group_id for (group_id, _) in timetable_swap.schedule.keys())
            group_id_to_pop = random.choice(list(group_ids_with_lessons))
            group_lessons = [key for key in timetable_swap.schedule.keys() if key[0] == group_id_to_pop]
            key_to_remove = random.choice(group_lessons)
            timetable_swap.schedule.pop(key_to_remove)

            # Now select another group to add a lesson to
            other_groups = [group for group in self.groups if group.group_id != group_id_to_pop]
            if other_groups:
                group_to_add = random.choice(other_groups)
                # Select a random subject from the group's subjects
                new_subject_name = random.choice(group_to_add.subjects)
                new_subject = self.subjects_dict[new_subject_name]
                # Select possible session types based on remaining hours
                possible_session_types = []
                if new_subject.lecture_hours > 0:
                    possible_session_types.append('Lecture')
                if new_subject.practice_hours > 0:
                    possible_session_types.append('Practice')
                if possible_session_types:
                    session_type = random.choice(possible_session_types)
                    # Select a random time slot
                    new_slot = random.choice(TIME_SLOTS)
                    # Select a random lecturer who can teach the subject and session type
                    suitable_lecturers = [
                        lect for lect in self.lecturers
                        if new_subject.name in lect.subjects and session_type in lect.subjects[new_subject.name]
                    ]
                    if suitable_lecturers:
                        new_lecturer = random.choice(suitable_lecturers)
                        # Select a random room that can accommodate the group
                        suitable_rooms = [room for room in self.rooms if room.capacity >= group_to_add.size]
                        if suitable_rooms:
                            new_room = random.choice(suitable_rooms)
                            # Check for conflicts
                            if self.is_assignment_valid(timetable_swap, group_to_add.group_id, new_slot, new_lecturer, new_room):
                                timetable_swap.schedule[(group_to_add.group_id, new_slot)] = (new_subject, new_lecturer, new_room, session_type)
                                if self.validate_schedule(timetable_swap):
                                    new_schedules.append(timetable_swap)
        # Return the list of valid new schedules
        return new_schedules

    def is_assignment_valid(self, timetable: Timetable, group_id: str, slot: Tuple[int, int],
                            lecturer: Lecturer, room: Room) -> bool:
        """
        Checks if assigning a lesson at the given slot for the group, lecturer, and room is valid.
        """
        # Check if the group already has a lesson at this slot
        if (group_id, slot) in timetable.schedule:
            return False

        # Check if the lecturer or room is occupied at this slot
        for (other_group_id, other_slot), (_, other_lecturer, other_room, _) in timetable.schedule.items():
            if other_slot == slot:
                if other_lecturer.name == lecturer.name or other_room.room_id == room.room_id:
                    return False
        return True

    def validate_schedule(self, timetable: Timetable) -> bool:
        """
        Validates the timetable to ensure it meets hard constraints.
        Returns True if valid, False otherwise.
        """
        violations = check_constraints(timetable, self.groups)
        return violations == 0
