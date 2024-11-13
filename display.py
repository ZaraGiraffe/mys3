from models import Timetable
from utils import schedule_to_csv

def display_schedule(timetable: Timetable, filename: str = "schedule.csv") -> None:
    schedule_to_csv(timetable, filename)
    print("Schedule displayed.")
