from typing import List, Dict, Tuple

class Group:
    def __init__(self, group_id: str, size: int, subjects: List[str]):
        self.group_id: str = group_id
        self.size: int = size
        self.subjects: List[str] = subjects

    def __repr__(self) -> str:
        return f"Group(id={self.group_id}, size={self.size}, subjects={self.subjects})"

class Subject:
    def __init__(self, name: str, total_hours: int):
        self.name: str = name
        self.total_hours: int = total_hours

    def __repr__(self) -> str:
        return f"Subject(name={self.name}, total_hours={self.total_hours})"

class Lecturer:
    def __init__(self, name: str, subjects: List[str], available_types: List[str]):
        self.name: str = name
        self.subjects: List[str] = subjects
        self.available_types: List[str] = available_types

    def __repr__(self) -> str:
        return f"Lecturer(name={self.name}, subjects={self.subjects}, available_types={self.available_types})"

class Room:
    def __init__(self, room_id: str, capacity: int):
        self.room_id: str = room_id
        self.capacity: int = capacity

    def __repr__(self) -> str:
        return f"Room(id={self.room_id}, capacity={self.capacity})"

class Timetable:
    def __init__(self):
        # Key: (group_id, (day, period))
        # Value: (Subject, Lecturer, Room)
        self.schedule: Dict[Tuple[str, Tuple[int, int]], Tuple[Subject, Lecturer, Room]] = {}

    def __repr__(self) -> str:
        return f"Timetable(schedule={self.schedule})"
