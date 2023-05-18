from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import ampermeter as amp
import power_supply as ps
import threading

hostName = "localhost"
serverPort = 8080

VOLTAGE_BEGIN = 0
VOLTAGE_END = 5
COUNT_OF_DOTS = 100
THREAD_STARTED = False
CURRENT_THREAD = 0
RECEIVED_VALUES = [1.2000000021, 1.7000002]


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query_components = parse_qs(urlparse(self.path).query)

        try:
            action_type = query_components['tp'][0]

            match action_type:

                case 'gt':
                    self.wfile.write(
                        bytearray((' '.join(str(e) for e in RECEIVED_VALUES)), encoding='utf-8'))

                case 'st':
                    if not THREAD_STARTED:
                        CURRENT_PROCESS = threading.Thread(target=startMeasure, args=(
                            VOLTAGE_BEGIN, VOLTAGE_END, COUNT_OF_DOTS))
                        CURRENT_PROCESS.start()
                    else:
                        self.send_error(
                            450, 'INTERNAL_ERROR', 'THREAD ALREADY STARTED, ONLY "SP" AND "GT" ACTION TYPES ALLOWED')

                case 'sp':
                    CURRENT_PROCESS.stop()

                case 'sts':
                    # Add additional check for max and min voltage
                    try:
                        voltage_begin = query_components["vb"][0]
                        voltage_end = query_components["ve"][0]
                        count_of_dots = query_components["mc"][0]

                        if not THREAD_STARTED:
                            CURRENT_PROCESS = threading.Thread(target=startMeasure, args=(
                                voltage_begin, voltage_end, count_of_dots))
                            CURRENT_PROCESS.start()
                        else:
                            self.send_error(
                                450, 'INTERNAL_ERROR', 'THREAD ALREADY STARTED, ONLY "SP" AND "GT" ACTION TYPES ALLOWED')

                    except Exception as e:
                        self.send_error(430, 'USER_ERROR',
                                        'ERROR HANDLING "STS" REQUEST PARAMS')

                case _:
                    self.send_error(420, 'USER_ERROR',
                                    'ACTION TYPE SPECIFIED INCORRECTLY')

        except Exception as e:
            self.send_error(410, 'USER_ERROR', 'ACTION NOT SPECIFIED')


def startMeasure(voltage_begin, voltage_end, count_of_dots):

    RECEIVED_VALUES = []

    ampermeter = amp.AMP()
    power_supply = ps.PS()

    for cur_voltage in range(voltage_begin, voltage_end, count_of_dots):
        power_supply.SET_VOLTAGE_DC(cur_voltage)
        tmp = ampermeter.READ_CURRENT_DC()
        RECEIVED_VALUES.append((cur_voltage, tmp))

    return 'CYCLE COMPLETED'.format(voltage_begin, voltage_end, count_of_dots)


if __name__ == "__main__":

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


# CODE:200 - SERVER RECEIVED REQUEST
# CODE:410 - ACTION NOT SPECIFIED
# CODE:420 - ACTION TYPE SPECIFIED INCORRECTLY
#
# ALLOWED ACTIONS:
#   "ST" - START MEASURE BY DEFAULT
#   "SP" - STOP MEASURE
#   "STS" - START WITH SETTING SPECIFIED BY USER: BEGINNING VOLTAGE, ENDING VOLTAGE, COUNT OF MEASURES
#   "GT" - RECEIVE FROM SERVER JSON FILE WITH VOLTAGE AND CURRENT
#
# CODE:430 - ERROR HANDLING "STS" REQUEST PARAMS
# CODE:450 - THREAD ALREADY STARTED, ONLY "SP" AND "GT" ACTION TYPES ALLOWED
