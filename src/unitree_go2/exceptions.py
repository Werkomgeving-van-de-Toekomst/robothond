"""Custom exceptions voor Unitree Go2 SDK"""


class Go2Error(Exception):
    """Basis exception voor alle Go2 fouten"""
    pass


class Go2ConnectionError(Go2Error):
    """Fout bij verbinden met de robot"""
    pass


class Go2CommandError(Go2Error):
    """Fout bij uitvoeren van commando"""
    pass


class Go2TimeoutError(Go2Error):
    """Timeout bij communicatie met robot"""
    pass

