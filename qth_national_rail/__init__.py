import asyncio
import datetime
import traceback
from argparse import ArgumentParser
from functools import partial

import qth

from zeep import Client as ZeepClient
from zeep.helpers import serialize_object

from .version import __version__


loop = asyncio.get_event_loop()
loop.set_debug(True)
client = None

qth_path = ""

start_station_code = "XXX"
end_station_code = "XXX"
api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
num_trains = 20

interval = 60

def get_trains_blocking():
    client = ZeepClient("https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01")
    return serialize_object(client.service.GetDepBoardWithDetails(
        numRows=num_trains,
        crs=start_station_code.upper(),
        filterCrs=end_station_code.upper(),
        _soapheaders={"AccessToken": api_key},
    ))

async def update_trains():
    try:
        trains = await loop.run_in_executor(None, get_trains_blocking)
        
        # Convert the only non-JSON serialisable type
        trains["generatedAt"] = str(trains["generatedAt"])
        
        await asyncio.wait([
            client.set_property(qth_path, [
                "{} ({})".format(service["std"],
                                 service["etd"])
                for service in (trains["trainServices"] or {}).get("service", [])
            ]),
            client.set_property(qth_path + "/detailed", trains),
        ])
        
        loop.call_later(interval, partial(loop.create_task, update_trains()))
    except (IOError, OSError):
        traceback.print_exc()
        loop.call_later(30, partial(loop.create_task, update_trains()))

async def async_main():
    await asyncio.wait([
        client.register(qth_path,
                        qth.PROPERTY_ONE_TO_MANY,
                        "Times of next train departures from {} to {}".format(
                            start_station_code, end_station_code),
                        delete_on_unregister=True),
        client.register(qth_path + "/detailed",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Details of train departures from {} to {}".format(
                            start_station_code, end_station_code),
                        delete_on_unregister=True),
    ])
    
    await update_trains()

def main():
    parser = ArgumentParser(
        description="Add National Rail Enquiries train departure boards to Qth.")
    parser.add_argument("apikey", help="National Rail Enquiries API key")
    parser.add_argument("start_station_code",
                        help="Starting station three-letter-code.")
    parser.add_argument("end_station_code",
                        help="Ending station three-letter-code.")
    parser.add_argument("--path", "-p", default="rail",
                        help="Qth path of rail times property to create. "
                             "(default %(default)s).")
    parser.add_argument("--number-of-trains", "-n", default=20, type=int,
                        help="Number of trains to fetch times for. "
                             "(default %(default)s).")
    parser.add_argument("--update-interval", "-i", default=60, type=float,
                        help="Update interval in seconds. "
                             "(default %(default)s).")
    
    parser.add_argument("--host", "-H", default=None,
                        help="Qth server hostname.")
    parser.add_argument("--port", "-P", default=None, type=int,
                        help="Qth server port.")
    parser.add_argument("--keepalive", "-K", default=10, type=int,
                        help="MQTT Keepalive interval (seconds).")
    parser.add_argument("--version", "-V", action="version",
                        version="%(prog)s {}".format(__version__))
    args = parser.parse_args()
    
    global client, qth_path, api_key, start_station_code, end_station_code, num_trains, interval
    
    client = qth.Client(
        "qth_national_rail", "Train departure times for Qth from National Rail Enquiries",
        host=args.host,
        port=args.port,
        keepalive=args.keepalive,
    )
    qth_path = args.path
    api_key = args.apikey
    start_station_code = args.start_station_code
    end_station_code = args.end_station_code
    num_trains = args.number_of_trains
    interval = args.update_interval
    
    loop.run_until_complete(async_main())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # Don't crash on Ctrl+C
        pass
