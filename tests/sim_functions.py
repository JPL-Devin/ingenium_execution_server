from test_util import *

def chill_eha_obj(channel_id):

    return {
      "channelIds": [
        channel_id
      ],
      "sessionId": 0,
      "channelTypes": [
        "FSW_REALTIME"
      ],
      "timeType": "SCLK",
      "startTime": "string",
      "endTime": "string",
      "timeout": 240,
      "inAlarm": "YELLOW_ALARM"
    }


def chill_evr_obj(evr_name):

    return {
      "sessionId": 0,
      "evrType": [
        "FSW_REALTIME"
      ],
      "evrName": evr_name,
      "eventId": 0,
      "evrLevel": "ACTIVITY_LO",
      "evrModule": "MODULE",
      "timeType": "SCLK",
      "startTime": "string",
      "endTime": "string",
      "timeout": 240
    }

def realtime_eha_obj(channel_id):

    return {
      "channelId": channel_id,
      "sessionId": 0,
      "startTime": "string",
      "endTime": "string",
      "minResults": 1
    }


def realtime_evr_obj(evr_name):

    return {
      "sessionId": 0,
      "evrName": evr_name,
      "eventId": 0,
      "evrLevel": "string",
      "startTime": "string",
      "endTime": "string",
      "minResults": 1
    }


def dp_obj(apid):

    return {
      "sessionId": 100,
      "dpStatus": "ALL",
      "apIds": [
        apid
      ],
      "timeType": "SCLK",
      "startTime": "string",
      "endTime": "string",
      "timeout": 240
    }


def cmd_fsw_sse(command):

    return {
      "sessionId": 50,
      "commandString": command,
      "validate": True,
      "timeout": 10
    }

def cmd_hw(command):

    return {
      "sessionId": 50,
      "commandStem": command,
      "timeout": 10
    }


def cmd_file(source, target):

    return {
      "sessionId": 0,
      "sourceFilePath": source,
      "targetFilePath": target,
      "fileType": 0,
      "overwrite": True,
      "timeout": 10
    }


def cmd_scmf(path):

    return {
      "sessionId": 0,
      "filePath": path,
      "disableChecks": False,
      "timeout": 10
    }


def forced_error_obj(endpoint, errorflag=None, errormsg=None, duration=None, delay_verify_evr=None, delay_verify_channels=None):

    if errormsg is None:
        errormsg = {}

    if duration is None:
        duration = 0
        
    if delay_verify_evr is None:
        delay_verify_evr = 0        

    if delay_verify_channels is None:
        delay_verify_channels = 0
        
    return {
      "endpoint": endpoint,
      "errorflag": errorflag,
      "errormsg": errormsg,
      "duration": duration,
      "delay_verify_evr": delay_verify_evr,
      "delay_verify_channels": delay_verify_channels
    }


def test_eha_obj(num, channel_id, dn_value):

    eha_obj = []

    for i in range(num):
        obj = {
            "dn": str(dn_value),
            "eu": 0,
            "channelId": channel_id,
            "sessionId": 0,
            "vcId": 0,
            "channelName": "string",
            "channelType": "SIGNED_INT",
            "channelStatus": "string",
            "sclk": get_current_time_str(),
            "ert": get_current_utc(),
            "scet": get_current_utc(),
            "isRecorded": True,
            "dnAlarmState": "string",
            "euAlarmState": "string"
          }
        eha_obj.append(obj)

    return eha_obj

def test_dp_obj(num, ap_id):
    dp_obj = []

    for i in range(num):
        obj = {
            "sessionId": 0,
            "vcId": 0,
            "dpStatus": "string",
            "apId": ap_id,
            "apIdProductType": "string",
            "filePath": "string",
            "fileSize": 0,
            "creationTime": "string",
            "sclk": get_current_time_str(),
            "ert": get_current_utc(),
            "scet": get_current_utc()
        }
        dp_obj.append(obj)

    return dp_obj

def test_evr_obj(num, evr_name, evr_message):
    evr_obj = []

    for i in range(num):
        obj = {
            "evrName": evr_name,
            "sessionId": 0,
            "vcId": 0,
            "eventId": 0,
            "evrLevel": "string",
            "fromSSE": True,
            "evrMessage": evr_message,
            "evrModule": "string",
            "sclk": get_current_time_str(),
            "ert": get_current_utc(),
            "scet": get_current_utc(),
            "isRecorded": True
          }
        evr_obj.append(obj)

    return evr_obj


def receipt_file():

    return {
      "uplink_type": "file",
      "channels": ic.binary_file_channels,
      "evrs": ic.binary_file_evr_name
    }

def receipt_fsw():

    return {
      "uplink_type": "immediate",
      "channels": ic.fsw_channels,
      "evrs": ic.fsw_evr_name
    }

def receipt_hw():

    return {
      "uplink_type": "hardware",
      "channels": ic.hw_channels,
      "evrs": ic.hw_evr_name
    }

def scmf_config(uplink_type, message):

    return {
      "type": uplink_type,
      "message": message
    }

def configurable_eha_value(dn_value, eu_value, channel_type, channel_id):

    return [
      {
        "dn": dn_value,
        "eu": eu_value,
        "channelId": channel_id,
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": channel_type,
        "channelStatus": "ENGAGE",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

def any_string_eha_channel(dn_value, channel_id):

    return [
      {
        "dn": dn_value,
        "eu": 0,
        "channelId": channel_id,
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "ASCII",
        "channelStatus": "ENGAGE",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

def string_eha_channel():

    return [
      {
        "dn": "0",
        "eu": 0,
        "channelId": "IMG-0261",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "STATUS",
        "channelStatus": "ENGAGE",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

def boolean_eha_channel():

    return [
      {
        "dn": "0",
        "eu": 0,
        "channelId": "WRX-0001",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "BOOLEAN",
        "channelStatus": "True",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

def integer_eha_channel():

    return [
      {
        "dn": "15",
        "eu": 10,
        "channelId": "CMD-1000",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "UNSIGNED_INT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

def signed_integer_eha_channel():

    return [
      {
        "dn": "15",
        "eu": 10,
        "channelId": "CMD-1001",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "SIGNED_INT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]


def float_eha_channel():

    return [
      {
        "dn": "10.5",
        "eu": 20.7,
        "channelId": "DMX-5000",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]



def bus_1553_alot_of_entries():
  
  entry = {
        "variable": "bus_binary",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "BIN",
        "data_value": "10101",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    }
  entries_list = []
  
  for num in range(0,100000):
    entries_list.append(entry)
  
  return entries_list

def configurable_bus_1553_entry(var_name, data_type, data_value, converted_value):

  return [
      {
        "variable": var_name,
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": data_type,
        "data_value": data_value,
        "converted_value": converted_value,
        "dictionary": "string",
        "log_file": "string"
    }
  ]

def bus_1553_binary():

  return [
      {
        "variable": "bus_binary",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "BIN",
        "data_value": "10101",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_binary",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "BIN",
        "data_value": "10101",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_binary",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "BIN",
        "data_value": "10111",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    }
  ]

def bus_1553_hex():

  return [
      {
        "variable": "bus_hex",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "HEX",
        "data_value": "0xDEAD",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_hex",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "HEX",
        "data_value": "0xDEAD",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_hex",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "HEX",
        "data_value": "0xDEED",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    }
  ]

def bus_1553_float():

  return [
      {
        "variable": "bus_float",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "1.23",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_float",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "1.23",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_float",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "2.5545",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    }
  ] 

def bus_1553_integer():

  return [
      {
        "variable": "bus_integer",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "INT",
        "data_value": "10",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_integer",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "INT",
        "data_value": "10",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_integer",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "INT",
        "data_value": "25",
        "converted_value": "",
        "dictionary": "string",
        "log_file": "string"
    }
  ] 

def bus_1553_enum():

  return [
      {
        "variable": "bus_enum",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "ENUM",
        "data_value": "1",
        "converted_value": "ROVER_START",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_enum",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "ENUM",
        "data_value": "1",
        "converted_value": "ROVER_START",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_enum",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "ENUM",
        "data_value": "5",
        "converted_value": "ROVER_STOP",
        "dictionary": "string",
        "log_file": "string"
    }
  ]  

def bus_1553_poly():

  return [
      {
        "variable": "bus_poly",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "11101",
        "converted_value": "0.5e-9",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_poly",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "11101",
        "converted_value": "0.5e-9",
        "dictionary": "string",
        "log_file": "string"
    },
      {
        "variable": "bus_poly",
        "rti": 0,
        "time_scet": "2018-208T12:00:00.000000",
        "time_sclk": "123",
        "bus_name": "string",
        "error_status": "string",
        "data_type": "FLOAT",
        "data_value": "10101",
        "converted_value": "1.5e-5",
        "dictionary": "string",
        "log_file": "string"
    }
  ]  





def graph_eha_test_data(length):

    graph = [
      {
        "dn": "10.5",
        "eu": 20.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      },
      {
        "dn": "12.5",
        "eu": 21.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      },
      {
        "dn": "14.5",
        "eu": 26.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      },
      {
        "dn": "18.5",
        "eu": 35.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      },
      {
        "dn": "20.5",
        "eu": 50.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      },
      {
        "dn": "50.5",
        "eu": 85.7,
        "channelId": "GRP-1500",
        "sessionId": 0,
        "vcId": 0,
        "channelName": "string",
        "channelType": "FLOAT",
        "channelStatus": "string",
        "sclk": get_current_time_str(),
        "ert": get_current_utc(),
        "scet": get_current_utc(),
        "isRecorded": True,
        "dnAlarmState": "string",
        "euAlarmState": "string"
      }
    ]

    return graph[:length]
