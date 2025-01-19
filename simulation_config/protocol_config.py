from air_ground_collaboration_02.air_protocol import AirProtocol as AirProtocolv2
from air_ground_collaboration_02.ground_protocol import GroundProtocol as GroundProtocolv2
from air_ground_collaboration_02.poi_protocol import PoIProtocol as PoIProtocolv2

from air_ground_collaboration_01.air_protocol import AirProtocol as AirProtocolv1
from air_ground_collaboration_01.ground_protocol import GroundProtocol as GroundProtocolv1
from air_ground_collaboration_01.poi_protocol import PoIProtocol as PoIProtocolv1

import importlib


def set_protocols(version):
    """
    Assigns the protocol versions dynamically.

    Parameters:
    - version (str): "v1" or "v2" to select the appropriate protocol version.

    Returns:
    - tuple: AirProtocol, GroundProtocol, and PoIProtocol as per the version.
    """
    if version == "v1":
        AirProtocol = AirProtocolv1
        GroundProtocol = GroundProtocolv1
        PoIProtocol = PoIProtocolv1
    elif version == "v2":
        AirProtocol = AirProtocolv2
        GroundProtocol = GroundProtocolv2
        PoIProtocol = PoIProtocolv2
    else:
        raise ValueError(f"Unknown version: {version}")

    return AirProtocol, GroundProtocol, PoIProtocol

def reconstruct_classes(serialized_classes):
    """
    Reconstructs classes from their string representations.

    Parameters:
    - serialized_classes (list of str): List of strings representing classes.

    Returns:
    - tuple: Tuple of classes.
    """
    classes = []
    for class_path in serialized_classes:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        classes.append(cls)
    return tuple(classes)