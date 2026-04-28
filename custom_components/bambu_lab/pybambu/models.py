"""
Model classes for PyBambu library
"""


class PrintJob:
    """Print job model"""

    def __init__(self, client):
        self.client = client
        self.print_percentage = 0
        self.gcode_state = ""
        self.remaining_time = 0
        self.current_layer = 0
        self.total_layers = 0

    def print_update(self, data):
        """Update print job from data"""
        raise NotImplementedError


class Info:
    """Info model"""

    def __init__(self, client):
        self.client = client
        self.sw_ver = ""
        self.device_type = ""
        self.active_nozzle_diameter = 0.0
        self.active_nozzle_type = ""
        self.left_nozzle_diameter = 0.0
        self.left_nozzle_type = ""
        self.right_nozzle_diameter = 0.0
        self.right_nozzle_type = ""
        self.door_open = False

    def info_update(self, data):
        """Update info from version data"""
        raise NotImplementedError

    def print_update(self, data):
        """Update info from print data"""
        raise NotImplementedError


class Extruder:
    """Extruder model"""

    def __init__(self, device):
        self.device = device
        self.active_nozzle_index = 0

    def print_update(self, data):
        """Update extruder from data"""
        raise NotImplementedError


class AMS:
    """AMS model"""

    def __init__(self, ams_id):
        self.id = ams_id
        self.humidity = 0
        self.temperature = 0.0
        self.sw_version = ""
        self.model = ""
        self.tray = []


class Tray:
    """Tray model"""

    def __init__(self):
        self.remain = 0
        self.type = ""
        self.color = ""
        self.tray_weight = ""


class AMSList:
    """AMS list model"""

    def __init__(self, client):
        self.client = client
        self.data = {}

    def info_update(self, data):
        """Update AMS list from version data"""
        raise NotImplementedError

    def print_update(self, data):
        """Update AMS list from print data"""
        raise NotImplementedError


class HMSList:
    """HMS error list model"""

    def __init__(self, client):
        self.client = client
        self.error_count = 0
        self.errors = {"Count": 0}

    def print_update(self, data):
        """Update HMS list from data"""
        raise NotImplementedError


class PrintError:
    """Print error model"""

    def __init__(self, client):
        self.client = client
        self.on = False
        self.error = None

    def print_update(self, data):
        """Update print error from data"""
        raise NotImplementedError


class Temperature:
    """Temperature model"""

    def __init__(self, client):
        self.client = client
        self.right_nozzle_temperature = 0
        self.right_nozzle_target_temperature = 0
        self.left_nozzle_temperature = 0
        self.left_nozzle_target_temperature = 0

    def print_update(self, data):
        """Update temperature from data"""
        raise NotImplementedError
