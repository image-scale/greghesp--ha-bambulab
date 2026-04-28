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

    # Map of module name prefixes to model names
    MODULE_MODELS = {
        "ams/": "AMS",
        "n3f/": "AMS 2 Pro",
        "n3s/": "AMS HT",
    }

    def __init__(self, ams_id):
        self.id = ams_id
        self.humidity = 0
        self.temperature = 0.0
        self.sw_version = ""
        self.model = ""
        self.tray = {}


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
        if "module" not in data:
            return False

        for module in data["module"]:
            name = module.get("name", "")
            sw_ver = module.get("sw_ver", "")

            # Parse AMS module names: "ams/0", "ams/1", "n3f/2", "n3s/128"
            for prefix, model_name in AMS.MODULE_MODELS.items():
                if name.startswith(prefix):
                    try:
                        ams_id = int(name[len(prefix):])
                        if ams_id not in self.data:
                            self.data[ams_id] = AMS(ams_id)
                        self.data[ams_id].sw_version = sw_ver
                        self.data[ams_id].model = model_name
                    except ValueError:
                        pass
                    break

        return True

    def print_update(self, data):
        """Update AMS list from print data"""
        if "ams" not in data:
            return False

        ams_data = data["ams"]
        if "ams" not in ams_data:
            return False

        for ams_entry in ams_data["ams"]:
            try:
                ams_id = int(ams_entry.get("id", "0"))
            except (ValueError, TypeError):
                continue

            # Get or create AMS
            if ams_id not in self.data:
                self.data[ams_id] = AMS(ams_id)

            ams = self.data[ams_id]

            # Parse humidity - use humidity_raw if available, otherwise humidity
            humidity_raw = ams_entry.get("humidity_raw")
            humidity = ams_entry.get("humidity")
            try:
                if humidity_raw is not None:
                    ams.humidity = int(humidity_raw)
                elif humidity is not None:
                    ams.humidity = int(humidity)
            except (ValueError, TypeError):
                pass

            # Parse temperature
            temp = ams_entry.get("temp")
            try:
                if temp is not None:
                    ams.temperature = float(temp)
            except (ValueError, TypeError):
                pass

            # Parse trays
            tray_list = ams_entry.get("tray", [])
            ams.tray = {}  # Reset trays
            for tray_data in tray_list:
                try:
                    tray_id = int(tray_data.get("id", "0"))
                except (ValueError, TypeError):
                    continue

                tray = Tray()
                tray.remain = tray_data.get("remain", 0)
                tray.type = tray_data.get("tray_type", "")
                tray.color = tray_data.get("tray_color", "")
                tray.tray_weight = tray_data.get("tray_weight", "")
                ams.tray[tray_id] = tray

        return True


class HMSList:
    """HMS error list model"""

    def __init__(self, client):
        self.client = client
        self.error_count = 0
        self.errors = {"Count": 0}
        self._prev_error_count = 0

    def print_update(self, data):
        """Update HMS list from data"""
        from .utils import get_HMS_error_text, get_HMS_severity

        if "hms" not in data:
            return False

        hms_list = data["hms"]

        # Get device info for printer model
        try:
            device_type = self.client._device.info.device_type
        except AttributeError:
            device_type = "unknown"

        # Get user language
        try:
            language = self.client.user_language
        except AttributeError:
            language = "en"

        # Build error dictionary
        new_errors = {"Count": 0}
        error_num = 0

        for hms_entry in hms_list:
            attr = hms_entry.get("attr", 0)
            code = hms_entry.get("code", 0)

            # Build HMS code: HMS_{attr>>16:04X}_{attr&0xFFFF:04X}_{code>>16:04X}_{code&0xFFFF:04X}
            hms_code = f"HMS_{(attr >> 16) & 0xFFFF:04X}_{attr & 0xFFFF:04X}_{(code >> 16) & 0xFFFF:04X}_{code & 0xFFFF:04X}"
            code_part = hms_code[4:]  # Remove "HMS_" prefix for wiki link

            # Get error text
            error_text = get_HMS_error_text(hms_code[4:], device_type, language)

            # Skip errors with empty text
            if not error_text or error_text == "":
                continue

            # Get severity
            severity = get_HMS_severity(hms_code[4:])

            error_num += 1
            new_errors[f"{error_num}-Code"] = hms_code
            new_errors[f"{error_num}-Error"] = error_text
            new_errors[f"{error_num}-Wiki"] = f"https://wiki.bambulab.com/en/x1/troubleshooting/hmscode/{code_part.replace('_', '_')}"
            new_errors[f"{error_num}-Severity"] = severity

        new_errors["Count"] = error_num
        self.error_count = error_num
        self.errors = new_errors

        # Check if error state changed
        state_changed = (error_num != self._prev_error_count) or (error_num > 0 and self._prev_error_count == 0)
        self._prev_error_count = error_num

        if state_changed and (error_num > 0 or self._prev_error_count == 0):
            try:
                self.client.callback("event_printer_error")
            except (AttributeError, TypeError):
                pass
            return True

        return False


class PrintError:
    """Print error model"""

    def __init__(self, client):
        self.client = client
        self.on = False
        self.error = None
        self._prev_error = None

    def print_update(self, data):
        """Update print error from data"""
        from .utils import get_print_error_text

        if "print_error" not in data:
            return False

        print_error = data["print_error"]

        # Get device info for printer model
        try:
            device_type = self.client._device.info.device_type
        except AttributeError:
            device_type = "unknown"

        # Get user language
        try:
            language = self.client.user_language
        except AttributeError:
            language = "en"

        if print_error == 0:
            # No error
            if self.on:
                # Error was cleared
                self.on = False
                self.error = None
                try:
                    self.client.callback("event_print_error")
                except (AttributeError, TypeError):
                    pass
            return False

        # Build error code: {print_error>>16:04X}_{print_error&0xFFFF:04X}
        error_code = f"{(print_error >> 16) & 0xFFFF:04X}_{print_error & 0xFFFF:04X}"

        # Get error text
        error_text = get_print_error_text(error_code, device_type, language)

        self.error = {
            "code": error_code,
            "error": error_text
        }
        self.on = True

        # Notify of error
        if self._prev_error != print_error:
            self._prev_error = print_error
            try:
                self.client.callback("event_print_error")
            except (AttributeError, TypeError):
                pass

        return False


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
        # H2D dual extruder temperature data is in device.extruder.info
        if "device" in data:
            device_data = data["device"]
            if "extruder" in device_data:
                extruder_data = device_data["extruder"]
                if "info" in extruder_data:
                    for ext_info in extruder_data["info"]:
                        ext_id = ext_info.get("id", 0)
                        temp_encoded = ext_info.get("temp", 0)

                        # Temperature is encoded as: (target << 16) | current
                        current_temp = temp_encoded & 0xFFFF
                        target_temp = temp_encoded >> 16

                        if ext_id == 0:
                            self.right_nozzle_temperature = current_temp
                            self.right_nozzle_target_temperature = target_temp
                        elif ext_id == 1:
                            self.left_nozzle_temperature = current_temp
                            self.left_nozzle_target_temperature = target_temp

        return True
