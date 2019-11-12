from UM.Message import Message

import requests

from .SessionManager import SessionManager


class DataApiService:
    data_api_url = "https://pu9tqbowx0.execute-api.eu-west-1.amazonaws.com/dev"

    def __init__(self):
        super().__init__()
        if DataApiService.__instance is not None:
            raise ValueError("Duplicate singleton creation")

        DataApiService._instance = self
        self._session_manager = SessionManager.getInstance()

    def sendGcode(self, gcode_path, gcode_name, serial_number):
        headers = {"Authorization": "Bearer {}".format(self._session_manager.getAccessToken())}
        files = {"file": (gcode_path, open(gcode_path, "rb"))}
        data = {"serialNumber": serial_number, "fileName": gcode_name}
        response = requests.post(self.data_api_url + "/gcodes", json=data, headers=headers)
        if 200 <= response.status_code < 300:
            response_message = response.json()
            presigned_url = response_message["url"]
            fields = response_message["fields"]
            response2 = requests.post(presigned_url, data=fields, files=files)
            if 200 <= response2.status_code < 300:
                message = Message("The gcode has been sent to the cloud successfully", title="Gcode sent")
                message.show()
            else:
                message = Message("There was an error sending the gcode to the cloud", title="Gcode sent error")
                message.show()
        else:
            message = Message("There was an error sending the gcode to the cloud", title="Gcode sent error")
            message.show()

    def getPrinters(self):
        headers = {"Authorization": "Bearer {}".format(self._session_manager.getAccessToken())}
        response = requests.get(self.data_api_url + "/printers", headers=headers)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            return []

    def getPrinter(self, serial_number: str):
        headers = {"Authorization": "Bearer {}".format(self._session_manager.getAccessToken())}
        response = requests.get(self.data_api_url + "/printers/" + serial_number, headers=headers)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            return {}

    @classmethod
    def getInstance(cls):
        if not DataApiService.__instance:
            DataApiService.__instance = cls()

        return DataApiService.__instance

    __instance = None
