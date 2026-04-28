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
        if "mc_percent" in data:
            self.print_percentage = data["mc_percent"]
        if "gcode_state" in data:
            self.gcode_state = data["gcode_state"]
        if "mc_remaining_time" in data:
            self.remaining_time = data["mc_remaining_time"]
        if "layer_num" in data:
            self.current_layer = data["layer_num"]
        if "total_layer_num" in data:
            self.total_layers = data["total_layer_num"]
        return True


class Info:
    """Info model"""

    # Nozzle type code to name mapping
    NOZZLE_TYPES = {
        "HS00": "stainless_steel",
        "HS01": "hardened_steel",
        "HH01": "high_flow_hardened_steel",
        "HX01": "hardened_steel",
        "HX05": "tungsten_carbide",
    }

    def __init__(self, client):
        self.client = client
        self.sw_ver = ""
        self.device_type = ""
        self._active_nozzle_diameter = 0.0
        self._active_nozzle_type = ""
        self.left_nozzle_diameter = 0.0
        self.left_nozzle_type = ""
        self.right_nozzle_diameter = 0.0
        self.right_nozzle_type = ""
        self.door_open = False
        self._nozzle_info = []  # Store nozzle info for dual extruder
        self._has_dual_nozzles = False

    @property
    def active_nozzle_diameter(self):
        """Get active nozzle diameter based on extruder state"""
        if self._has_dual_nozzles:
            try:
                extruder = self.client._device.extruder
                active_idx = extruder.active_nozzle_index
                if active_idx == 0:
                    return self.right_nozzle_diameter
                else:
                    return self.left_nozzle_diameter
            except (AttributeError, KeyError):
                pass
        return self._active_nozzle_diameter

    @active_nozzle_diameter.setter
    def active_nozzle_diameter(self, value):
        """Set active nozzle diameter"""
        self._active_nozzle_diameter = value

    @property
    def active_nozzle_type(self):
        """Get active nozzle type based on extruder state"""
        if self._has_dual_nozzles:
            try:
                extruder = self.client._device.extruder
                active_idx = extruder.active_nozzle_index
                if active_idx == 0:
                    return self.right_nozzle_type
                else:
                    return self.left_nozzle_type
            except (AttributeError, KeyError):
                pass
        return self._active_nozzle_type

    @active_nozzle_type.setter
    def active_nozzle_type(self, value):
        """Set active nozzle type"""
        self._active_nozzle_type = value

    def info_update(self, data):
        """Update info from version data"""
        if "module" in data:
            for module in data["module"]:
                if module.get("name") == "ota":
                    self.sw_ver = module.get("sw_ver", "")
                    break
        return True

    def print_update(self, data):
        """Update info from print data"""
        # Handle nozzle info for single extruder printers (P1P, etc.)
        if "nozzle_diameter" in data:
            diameter = data["nozzle_diameter"]
            if isinstance(diameter, str):
                diameter = float(diameter)
            self._active_nozzle_diameter = diameter
            self.right_nozzle_diameter = diameter

        if "nozzle_type" in data:
            self._active_nozzle_type = data["nozzle_type"]
            self.right_nozzle_type = data["nozzle_type"]

        # Handle dual-extruder nozzle info (H2D)
        if "device" in data:
            device_data = data["device"]
            if "nozzle" in device_data:
                nozzle_data = device_data["nozzle"]
                if "info" in nozzle_data:
                    self._nozzle_info = nozzle_data["info"]
                    # Check if this is a dual nozzle setup
                    if len(self._nozzle_info) >= 2:
                        self._has_dual_nozzles = True
                    for nozzle in self._nozzle_info:
                        nozzle_id = nozzle.get("id", 0)
                        diameter = nozzle.get("diameter", 0.0)
                        nozzle_type_code = nozzle.get("type", "")
                        nozzle_type = self.NOZZLE_TYPES.get(nozzle_type_code, nozzle_type_code)

                        if nozzle_id == 0:
                            self.right_nozzle_diameter = diameter
                            self.right_nozzle_type = nozzle_type
                        elif nozzle_id == 1:
                            self.left_nozzle_diameter = diameter
                            self.left_nozzle_type = nozzle_type

        # Handle door status - H2D uses stat field
        if "stat" in data:
            stat_str = data["stat"]
            try:
                stat = int(stat_str, 16)
                # Bit 23 (0x800000) indicates door open
                self.door_open = bool(stat & 0x800000)
            except (ValueError, TypeError):
                pass

        return True


class Extruder:
    """Extruder model"""

    def __init__(self, device):
        self.device = device
        self.active_nozzle_index = 0

    def print_update(self, data):
        """Update extruder from data"""
        # Check for device.extruder.state
        if "device" in data:
            device_data = data["device"]
            if "extruder" in device_data:
                extruder_data = device_data["extruder"]
                if "state" in extruder_data:
                    state = extruder_data["state"]
                    # Active nozzle index is bit 8 of state
                    self.active_nozzle_index = (state >> 8) & 1
        return True


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
