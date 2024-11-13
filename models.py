# models.py

from typing import List, Dict, Tuple

class Group:
    def __init__(self, group_id: str, size: int, subjects: List[str]):
        self.group_id: str = group_id
        self.size: int = size
        self.subjects: List[str] = subjects

    def __repr__(self) -> str:
        return f"Group(id={self.group_id}, size={self.size}, subjects={self.subjects})"

class Subject:
    def __init__(self, name: str, lecture_hours: int, practice_hours: int):
        self.name: str = name
        self.lecture_hours: int = lecture_hours
        self.practice_hours: int = practice_hours

    def __repr__(self) -> str:
        return f"Subject(name={self.name}, lecture_hours={self.lecture_hours}, practice_hours={self.practice_hours})"

class Lecturer:
    def __init__(self, lecturer_id: str, name: str):
        self.lecturer_id: str = lecturer_id
        self.name: str = name
        self.subjects: Dict[str, List[str]] = {}  # subject_name -> list of available_types (Lecture, Practice)

    def __repr__(self) -> str:
        return f"Lecturer(id={self.lecturer_id}, name={self.name}, subjects={self.subjects})"

class Room:
    def __init__(self, room_id: str, capacity: int):
        self.room_id: str = room_id
        self.capacity: int = capacity

    def __repr__(self) -> str:
        return f"Room(id={self.room_id}, capacity={self.capacity})"

class Timetable:
    def __init__(self):
        # Key: (group_id, (day, period))
        # Value: (Subject, Lecturer, Room, Session Type)
        self.schedule: Dict[Tuple[str, Tuple[int, int]], Tuple[Subject, Lecturer, Room, str]] = {}

    def __repr__(self) -> str:
        return f"Timetable(schedule={self.schedule})"
