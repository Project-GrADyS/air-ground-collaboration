from A2G_Coord_v1.air_protocol import AirProtocol as AirProtocolv1
from A2G_Coord_v1.ground_protocol import GroundProtocol as GroundProtocolv1
from A2G_Coord_v1.poi_protocol import PoIProtocol as PoIProtocolv1

from A2G_Coord_v2.air_protocol import AirProtocol as AirProtocolv2
from A2G_Coord_v2.ground_protocol import GroundProtocol as GroundProtocolv2
from A2G_Coord_v2.poi_protocol import PoIProtocol as PoIProtocolv2

from A2G_Coord_v3.air_protocol import AirProtocol as AirProtocolv3
from A2G_Coord_v3.ground_protocol import GroundProtocol as GroundProtocolv3
from A2G_Coord_v3.poi_protocol import PoIProtocol as PoIProtocolv3

import importlib
import json


def set_algorithms(version):
    """
    Assigns the algorithm versions dynamically.

    Parameters:
    - version (str): "v1", "v2" or "v3" to select the appropriate algorithm version.

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
    elif version == "v3":
        AirProtocol = AirProtocolv3
        GroundProtocol = GroundProtocolv3
        PoIProtocol = PoIProtocolv3
    else:
        raise ValueError(f"Unknown version: {version}")

    return AirProtocol, GroundProtocol, PoIProtocol

def serialize_algorithms(classes):
    """
    Serializes classes.

    Parameters:
    - classes (list of classes): Tuple of classes.

    Returns:
    - str: List of strings representing classes.
    """
    return json.dumps([f"{cls.__module__}.{cls.__name__}" for cls in classes])

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