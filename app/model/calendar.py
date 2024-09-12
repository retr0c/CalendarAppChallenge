from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List, Dict
from app.services.util import generate_unique_id, reminder_not_found_error, slot_not_available_error, event_not_found_error, date_lower_than_today_error

@dataclass
class Reminder:
    EMAIL = "email"
    SYSTEM = "system"

    date_time: datetime
    type: str = EMAIL

    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"

@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time
    reminders: List[Reminder] = field(default_factory=list)
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time: datetime, type_: str = Reminder.EMAIL):
        reminder = Reminder(date_time=date_time, type=type_)
        self.reminders.append(reminder)

    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            del self.reminders[reminder_index]
        else:
            reminder_not_found_error()

    def __str__(self):
        return f"ID: {self.id}\nEvent title: {self.title}\nDescription: {self.description}\nTime: {self.start_at} - {self.end_at}"

class Day:
    def __init__(self, date_: date):
        self.date_ = date_
        self.slots = {}
        self._init_slots()

    def _init_slots(self):
        start = time(0, 0)
        while start < time(23, 45):
            self.slots[start] = None
            start = (datetime.combine(datetime.today(), start) + timedelta(minutes=15)).time()

    def add_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot] is not None:
                    slot_not_available_error()
                self.slots[slot] = event_id

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id

class Calendar:
    def __init__(self):
        self.days: Dict[date, Day] = {}
        self.events: Dict[str, Event] = {}

    def add_event(self, title: str, description: str, date_: date, start_at: time, end_at: time) -> str:
        if date_ < datetime.now().date():
            date_lower_than_today_error()
        
        if date_ not in self.days:
            self.days[date_] = Day(date_)
        
        event = Event(title=title, description=description, date_=date_, start_at=start_at, end_at=end_at)
        self.days[date_].add_event(event.id, start_at, end_at)
        self.events[event.id] = event
        return event.id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str = Reminder.EMAIL):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()
        event.add_reminder(date_time=date_time, type_=type_)

    def find_available_slots(self, date_: date) -> List[time]:
        available_slots = []
        day = self.days.get(date_)
        if day:
            for slot, event_id in day.slots.items():
                if event_id is None:
                    available_slots.append(slot)
        return available_slots

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        is_new_date = False
        if event.date_ != date_:
            self.delete_event(event_id)
            event = Event(title=title, description=description, date_=date_, start_at=start_at, end_at=end_at)
            event.id = event_id
            self.events[event_id] = event
            is_new_date = True
            if date_ not in self.days:
                self.days[date_] = Day(date_)
            day = self.days[date_]
            day.add_event(event_id, start_at, end_at)
        else:
            event.title = title
            event.description = description
            event.date_ = date_
            event.start_at = start_at
            event.end_at = end_at

        for day in self.days.values():
            if not is_new_date and event_id in day.slots.values():
                day.delete_event(event.id)
                day.update_event(event.id, start_at, end_at)

    def delete_event(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()

        self.events.pop(event_id)
        for day in self.days.values():
            if event_id in day.slots.values():
                day.delete_event(event_id)
                break

    def find_events(self, start_at: date, end_at: date) -> Dict[date, List[Event]]:
        events: Dict[date, List[Event]] = {}
        for event in self.events.values():
            if start_at <= event.date_ <= end_at:
                if event.date_ not in events:
                    events[event.date_] = []
                events[event.date_].append(event)
        return events

    def delete_reminder(self, event_id: str, reminder_index: int):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()
        event.delete_reminder(reminder_index)

    def list_reminders(self, event_id: str) -> List[Reminder]:
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()
        return event.reminders
