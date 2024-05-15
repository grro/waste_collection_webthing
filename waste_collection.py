import logging
import os
from ics import Calendar
from threading import Thread
from datetime import datetime, timedelta
from time import sleep
from typing import List



def day_granularity(date: datetime) -> datetime:
    return datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d")


class Date:

    def __init__(self, date: datetime):
        self.date = date

    def is_soon(self) -> bool:
        return (self.date - day_granularity(datetime.now())).days <= 1

    def reminder(self) -> str:
        days = (self.date - day_granularity(datetime.now())).days
        if days < 1:
            return "heute"
        elif days < 2:
            return "morgen"
        elif days < 7:
            return "am " + {"Sun": "So", "Mon": "Mo", "Tue": "Di", "Wed": "Mi", "Thu": "Do", "Fri": "Fr", "Sat": "Sa"}.get(self.date.strftime("%a"))
        else:
            return "in " + str(days) + " T."






class WasteCollectionSchedule:

    def __init__(self, directory: str):
        self.__is_running = True
        self.__listener = lambda: None    # "empty" listener
        self.directory = directory
        self.organic_timeseries = []
        self.recycling_timeseries = []
        self.residual_timeseries = []
        self.paper_timeseries = []
        self.__reload()

    def set_listener(self,listener):
        self.__listener = listener

    @property
    def next_organic(self) -> datetime:
        return self.__next(self.organic_timeseries)

    @property
    def next_recycling(self) -> datetime:
        return self.__next(self.recycling_timeseries)

    @property
    def next_paper(self) -> datetime:
        return self.__next(self.paper_timeseries)

    @property
    def next_residual(self) -> datetime:
        return self.__next(self.residual_timeseries)

    def __next(self, timeseries : List[datetime]) -> datetime:
        for date in timeseries:
            if date >= (datetime.now() - timedelta(hours=8)):
                return date

    def __scan_ics_files(self):
        files = []
        for file in os.listdir(self.directory):
            if file.endswith('.ics'):
                files.append(os.path.join(self.directory, file))
        return files

    def __read_ics_file(self, filename: str):
        ignore_section = False
        content = ""
        with open(filename, 'r') as file:
            for line in file.readlines():
                if line.startswith("BEGIN:VALARM"):
                    ignore_section = True
                elif line.startswith("END:VALARM"):
                    ignore_section = False
                elif not ignore_section:
                    content = content + line
        return content

    def __reload(self):
        new_recycling_timeseries = []
        new_organic_timeseries = []
        new_residual_timeseries = []
        new_paper_timeseries = []

        for file in self.__scan_ics_files():
            num_loaded = 0
            try:
                logging.info("parsing " + file)
                content = self.__read_ics_file(file)
                c = Calendar(content)
                for event in c.events:
                    num_loaded += 1
                    date = day_granularity(event.begin.datetime)
                    topic = event.name
                    if 'bio' in topic.lower():
                        new_organic_timeseries.append(date)
                    elif 'wertstoff' in topic.lower():
                        new_recycling_timeseries.append(date)
                    elif 'papier' in topic.lower():
                        new_paper_timeseries.append(date)
                    elif 'rest' in topic.lower():
                        new_residual_timeseries.append(date)
                logging.debug(str(num_loaded) + " reminders loaded for " + file)
            except Exception as e:
                logging.warning("error occurred parsing " + file + " " + str(e))

        self.recycling_timeseries = sorted(new_recycling_timeseries)
        self.organic_timeseries = sorted(new_organic_timeseries)
        self.residual_timeseries = sorted(new_residual_timeseries)
        self.paper_timeseries = sorted(new_paper_timeseries)
        self.__listener()

    def start(self):
        Thread(target=self.__reload_loop, daemon=True).start()

    def stop(self):
        self.__is_running = False

    def __reload_loop(self):
        while self.__is_running:
            try:
                self.__reload()
                sleep(12*59)
            except Exception as e:
                logging.warning("error occurred on sync " + str(e))
