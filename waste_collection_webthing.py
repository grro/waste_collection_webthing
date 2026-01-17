import sys
from datetime import datetime
import logging
import tornado.ioloop
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from waste_collection import WasteCollectionSchedule
from waste_collection_mcp import WasteCollectionScheduleMCPServer




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





class WasteCollectionScheduleThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, description: str, schedule: WasteCollectionSchedule):
        Thing.__init__(
            self,
            'urn:dev:ops:waste_collection_schedule-1',
            'WasteCollectionSchedule2',
            ['MultiLevelSensor'],
            description
        )
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.schedule = schedule
        self.schedule.set_listener(self.on_value_changed)

        self.next_organic = Value(schedule.next_organic)
        self.add_property(
            Property(self,
                     'next_organic',
                     self.next_organic,
                     metadata={
                         'title': 'next_organic',
                         "type": "datetime",
                         'description': 'the datetime of the next organic collection',
                         'readOnly': True,
                     }))

        self.next_organic_reminder = Value("")
        self.add_property(
            Property(self,
                     'next_organic_reminder',
                     self.next_organic_reminder,
                     metadata={
                         'title': 'next_organic_reminder',
                         "type": "string",
                         'description': 'the next collection message',
                         'readOnly': True,
                     }))

        self.next_organic_soon = Value(False)
        self.add_property(
            Property(self,
                     'next_organic_soon',
                     self.next_organic_soon,
                     metadata={
                         'title': 'next_organic_soon',
                         "type": "boolean",
                         'description': 'true if soon',
                         'readOnly': True,
                     }))

        self.next_organic = Value(schedule.next_organic)
        self.add_property(
            Property(self,
                     'next_organic',
                     self.next_organic,
                     metadata={
                         'title': 'next_organic',
                         "type": "datetime",
                         'description': 'the datetime of the next organic collection',
                         'readOnly': True,
                     }))

        self.next_recycling_reminder = Value("")
        self.add_property(
            Property(self,
                     'next_recycling_reminder',
                     self.next_recycling_reminder,
                     metadata={
                         'title': 'next_recycling_reminder',
                         "type": "string",
                         'description': 'the next collection message',
                         'readOnly': True,
                     }))

        self.next_recycling_soon = Value(False)
        self.add_property(
            Property(self,
                     'next_recycling_soon',
                     self.next_recycling_soon,
                     metadata={
                         'title': 'next_recycling_soon',
                         "type": "boolean",
                         'description': 'true if soon',
                         'readOnly': True,
                     }))

        self.next_recycling = Value(schedule.next_recycling)
        self.add_property(
            Property(self,
                     'next_recycling',
                     self.next_recycling,
                     metadata={
                         'title': 'next_recycling',
                         "type": "datetime",
                         'description': 'the datetime of the next recycling collection',
                         'readOnly': True,
                     }))

        self.next_paper_reminder = Value("")
        self.add_property(
            Property(self,
                     'next_paper_reminder',
                     self.next_paper_reminder,
                     metadata={
                         'title': 'next_paper_reminder',
                         "type": "string",
                         'description': 'the next collection message',
                         'readOnly': True,
                     }))

        self.next_paper_soon = Value(False)
        self.add_property(
            Property(self,
                     'next_paper_soon',
                     self.next_paper_soon,
                     metadata={
                         'title': 'next_paper_soon',
                         "type": "boolean",
                         'description': 'true if soon',
                         'readOnly': True,
                     }))

        self.next_paper = Value(schedule.next_paper)
        self.add_property(
            Property(self,
                     'next_paper',
                     self.next_paper,
                     metadata={
                         'title': 'next_paper',
                         "type": "datetime",
                         'description': 'the datetime of the next paper collection',
                         'readOnly': True,
                     }))

        self.next_residual_reminder = Value("")
        self.add_property(
            Property(self,
                     'next_residual_reminder',
                     self.next_residual_reminder,
                     metadata={
                         'title': 'next_residual_reminder',
                         "type": "string",
                         'description': 'the next collection message',
                         'readOnly': True,
                     }))

        self.next_residual_soon = Value(False)
        self.add_property(
            Property(self,
                     'next_residual_soon',
                     self.next_residual_soon,
                     metadata={
                         'title': 'next_residual_soon',
                         "type": "boolean",
                         'description': 'true if soon',
                         'readOnly': True,
                     }))

        self.next_residual = Value(schedule.next_residual)
        self.add_property(
            Property(self,
                     'next_residual',
                     self.next_organic,
                     metadata={
                         'title': 'next_residual',
                         "type": "datetime",
                         'description': 'the datetime of the next residual collection',
                         'readOnly': True,
                     }))


        self.scanned_ics_files = Value(",".join(schedule.scanned_ics_files))
        self.add_property(
            Property(self,
                     'scanned_ics_files',
                     self.scanned_ics_files,
                     metadata={
                         'title': 'scanned_ics_files',
                         "type": "string",
                         'description': 'the scanned ics files',
                         'readOnly': True,
                     }))


    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def __is_soon(self, dt: datetime) -> bool:
        return (dt - day_granularity(datetime.now())).days <= 1

    def __reminder(self, dt: datetime) -> str:
        days = (dt - day_granularity(datetime.now())).days
        if days < 1:
            return "heute"
        elif days < 2:
            return "morgen"
        elif days < 7:
            return "am " + {"Sun": "So", "Mon": "Mo", "Tue": "Di", "Wed": "Mi", "Thu": "Do", "Fri": "Fr", "Sat": "Sa"}.get(dt.strftime("%a"))
        else:
            return "in " + str(days) + " T."

    def _on_value_changed(self):
        try:
            self.next_organic_soon.notify_of_external_update(self.__is_soon(self.schedule.next_organic))
            self.next_organic.notify_of_external_update(self.schedule.next_organic.strftime("%Y-%m-%d"))
            self.next_organic_reminder.notify_of_external_update(self.__reminder(self.schedule.next_organic))

            self.next_recycling_soon.notify_of_external_update(self.__is_soon(self.schedule.next_recycling))
            self.next_recycling.notify_of_external_update(self.schedule.next_recycling.strftime("%Y-%m-%d"))
            self.next_recycling_reminder.notify_of_external_update(self.__reminder(self.schedule.next_recycling))

            self.next_residual_soon.notify_of_external_update(self.__is_soon(self.schedule.next_residual))
            self.next_residual.notify_of_external_update(self.schedule.next_residual.strftime("%Y-%m-%d"))
            self.next_residual_reminder.notify_of_external_update(self.__reminder(self.schedule.next_residual))

            self.next_paper_soon.notify_of_external_update(self.__is_soon(self.schedule.next_paper))
            self.next_paper.notify_of_external_update(self.schedule.next_paper.strftime("%Y-%m-%d"))
            self.next_paper_reminder.notify_of_external_update(self.__reminder(self.schedule.next_paper))

            self.scanned_ics_files.notify_of_external_update(", ".join(self.schedule.scanned_ics_files))
        except Exception as e:
            logging.warning("error occurred " + str(e))


def run_server(description: str, port: int, directory: str):
    schedule = WasteCollectionSchedule(directory)
    server = WebThingServer(SingleThing(WasteCollectionScheduleThing(description, schedule)), port=port, disable_host_validation=True)
    mcp_server = WasteCollectionScheduleMCPServer("WasteCollectionSchedule", port=port+2, schedule=schedule)

    try:
        logging.info('starting the server http://localhost:' + str(port) + " (directory=" + directory + ")")
        schedule.start()
        mcp_server.start()
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        schedule.stop()
        mcp_server.stop()
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), sys.argv[2])




'''
<div>
    <div ng-if="itemValue('ResidualWasteSoon') == 'ON'" class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_black.png"   width="60" height="67"></img>
      <span style="color: white; font-size: 10pt; font-weight: bold">Restm. {{itemValue('ResidualWasteDate')}}</span>
    </div>
     <div ng-if="itemValue('ResidualWasteSoon') !='ON'" class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_grey.png"   width="60" height="67"></img>
      <span style="color: #34485B; font-size: 10pt">Restm. {{itemValue('ResidualWasteDate')}}</span>
    </div>
    <div ng-if="itemValue('OrganicWasteSoon') =='ON'" class="col-xs-12 col-sm-12 col-md-12 col-lg-11 text-left">
      <img src="/static/icons/trash_green.png"   width="60" height="67"></img>
      <span style="color: lightgreen; font-size: 10pt; font-weight: bold">Bio {{itemValue('OrganicWasteDate')}}</span>
    </div> 
	  <div  ng-if="itemValue('OrganicWasteSoon') !='ON'" class="col-xs-12 col-sm-12 col-md-12 col-lg-11 text-left">
      <img src="/static/icons/trash_grey.png"  width="60" height="67"></img>
      <span style="color: #34485B; font-size: 10pt;">Bio {{itemValue('OrganicWasteDate')}}</span>
    </div>   
    <div ng-if="itemValue('PaperWasteSoon') == 'ON'" class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_brown.png"  width="60" height="67"></img>
      <span style="color: brown; font-size: 10pt; font-weight: bold">Papier {{itemValue('PaperWasteDate')}}</span>
    </div>
    <div ng-if="itemValue('PaperWasteSoon') != 'ON'"  class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_grey.png"  width="60" height="67"></img>
      <span style="color: #34485B; font-size: 10pt">Papier {{itemValue('PaperWasteDate')}}</span>
    </div>
      <div ng-if="itemValue('RecyclingWasteSoon') == 'ON'"  class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_yellow.png"  width="60" height="67"></img>
      <span style="color: yellow; font-size: 10pt; font-weight: bold">Wertst. {{itemValue('RecyclingWasteDate')}}</span>
    </div>
    <div ng-if="itemValue('RecyclingWasteSoon') != 'ON'" class="col-xs-12 col-sm-12  col-md-12 col-lg-12 text-left">
      <img src="/static/icons/trash_grey.png"  width="60" height="67"></img>
      <span style="color: #34485B; font-size: 10pt">Wertst. {{itemValue('RecyclingWasteDate')}}</span>
    </div>
</div>

'''
