import sys
import logging
import tornado.ioloop
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from waste_collection import WasteCollectionSchedule




class WasteCollectionScheduleThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, description: str, schedule: WasteCollectionSchedule):
        Thing.__init__(
            self,
            'urn:dev:ops:waste_collection_schedule-1',
            'WasteCollectionSchedule',
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
                         'description': 'the datetime of the next organaic collection',
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


    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def _on_value_changed(self):
        self.next_organic.notify_of_external_update(self.schedule.next_organic.strftime("%Y-%m-%d"))
        self.next_recycling.notify_of_external_update(self.schedule.next_recycling.strftime("%Y-%m-%d"))
        self.next_residual.notify_of_external_update(self.schedule.next_residual.strftime("%Y-%m-%d"))
        self.next_paper.notify_of_external_update(self.schedule.next_paper.strftime("%Y-%m-%d"))


def run_server(description: str, port: int, directory: str):
    schedule = WasteCollectionSchedule(directory)
    server = WebThingServer(SingleThing(WasteCollectionScheduleThing(description, schedule)), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server http://localhost:' + str(port) + " (directory=" + directory + ")")
        schedule.start()
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        schedule.stop()
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), sys.argv[2])
