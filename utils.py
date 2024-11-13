import csv
import os
import random
from models import Timetable, Group, Subject, Lecturer, Room
from typing import List, Dict, Tuple
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

TIME_SLOTS: List[Tuple[int, int]] = [(day, period) for day in range(5) for period in range(4)]
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def load_data() -> Tuple[List[Group], List[Subject], List[Lecturer], List[Room]]:
    groups: List[Group] = []
    subjects: Dict[str, Subject] = {}
    lecturers_dict: Dict[str, Lecturer] = {}
    lecturers: List[Lecturer] = []
    rooms: List[Room] = []

    with open("data/subjects.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subject = Subject(
                name=row["name"],
                lecture_hours=int(row["lecture_hours"]),
                practice_hours=int(row["practice_hours"])
            )
            subjects[subject.name] = subject

    with open("data/groups.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subjects_list = [s.strip() for s in row["subjects"].split(",")]
            group = Group(
                group_id=row["group_id"],
                size=int(row["size"]),
                subjects=subjects_list
            )
            groups.append(group)

    with open("data/lecturers.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            lecturer_id = row["lecturer_id"]
            name = row["name"]
            subject_name = row["subject"].strip()
            available_type = row["available_type"].strip()

            if lecturer_id not in lecturers_dict:
                lecturer = Lecturer(lecturer_id=lecturer_id, name=name)
                lecturers_dict[lecturer_id] = lecturer
            else:
                lecturer = lecturers_dict[lecturer_id]

            if subject_name not in lecturer.subjects:
                lecturer.subjects[subject_name] = []
            lecturer.subjects[subject_name].append(available_type)

    lecturers = list(lecturers_dict.values())

    with open("data/rooms.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            room = Room(
                room_id=row["room_id"],
                capacity=int(row["capacity"])
            )
            rooms.append(room)

    return groups, list(subjects.values()), lecturers, rooms

def check_constraints(timetable: Timetable, groups: List[Group]) -> int:
    violations = 0
    lecturer_schedule: Dict[Tuple[str, Tuple[int, int]], bool] = {}
    room_schedule: Dict[Tuple[str, Tuple[int, int]], bool] = {}
    group_schedule: Dict[Tuple[str, Tuple[int, int]], bool] = {}

    for (group_id, slot), (subject, lecturer, room, session_type) in timetable.schedule.items():
        if group_schedule.get((group_id, slot)):
            violations += 1 
        else:
            group_schedule[(group_id, slot)] = True

        if lecturer_schedule.get((lecturer.name, slot)):
            violations += 1
        else:
            lecturer_schedule[(lecturer.name, slot)] = True

        if room_schedule.get((room.room_id, slot)):
            violations += 1
        else:
            room_schedule[(room.room_id, slot)] = True

    return violations

def schedule_to_csv(timetable: Timetable, filename: str = "schedule.csv") -> None:
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Group ID", "Day", "Period", "Subject", "Lecturer", "Room ID", "Session Type"])

        for (group_id, (day, period)), (subject, lecturer, room, session_type) in timetable.schedule.items():
            writer.writerow([group_id, day, period, subject.name, lecturer.name, room.room_id, session_type])
    print(f"Schedule saved to {filename}")

def save_schedule_to_excel(timetable: Timetable, output_folder: str = "schedules") -> None:
    import os
    from openpyxl import Workbook

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    groups = set(group_id for (group_id, _) in timetable.schedule.keys())

    for group_id in groups:
        wb = Workbook()
        ws = wb.active
        ws.title = f"Group {group_id}"

        for col_num, day in enumerate(DAYS_OF_WEEK, start=2): 
            col_letter = get_column_letter(col_num)
            ws[f"{col_letter}1"] = day

        for row_num in range(2, 6): 
            ws[f"A{row_num}"] = f"Period {row_num - 1}"

        for (gid, (day, period)), (subject, lecturer, room, session_type) in timetable.schedule.items():
            if gid == group_id:
                col_num = day + 2 
                row_num = period + 2 
                col_letter = get_column_letter(col_num)
                cell = f"{col_letter}{row_num}"
                ws[cell] = f"{subject.name} : {lecturer.name} : {room.room_id} :: {session_type}"

        filename = os.path.join(output_folder, f"group_{group_id}.xlsx")
        wb.save(filename)
        print(f"Schedule for Group {group_id} saved to {filename}")