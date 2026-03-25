"""handlers/singleband.py

Handle /singleband API endpoint.
"""

from typing import Sequence, Mapping, Union, Tuple, Optional, TypeVar, cast, Any, Dict
from typing.io import BinaryIO

import collections
from collections import OrderedDict

from terracotta import get_settings, get_driver, image, xyz
from terracotta.profile import trace

Number = TypeVar("Number", int, float)
NumberOrString = TypeVar("NumberOrString", int, float, str)
ListOfRanges = Sequence[
    Optional[Tuple[Optional[NumberOrString], Optional[NumberOrString]]]
]
RGBA = Tuple[Number, Number, Number, Number]


@trace("singleband_handler")
def singleband(
    keys: Union[Sequence[str], Mapping[str, str]],
    tile_xyz: Optional[Tuple[int, int, int]] = None,
    *,
    colormap: Union[str, Mapping[Number, RGBA], None] = None,
    stretch_range: Optional[Tuple[NumberOrString, NumberOrString]] = None,
    tile_size: Optional[Tuple[int, int]] = None
) -> BinaryIO:
    """Return singleband image as PNG"""

    cmap_or_palette: Union[str, Sequence[RGBA], None]

    if stretch_range is None:
        stretch_min, stretch_max = None, None
    else:
        stretch_min, stretch_max = stretch_range

    preserve_values = isinstance(colormap, collections.abc.Mapping)

    settings = get_settings()
    if tile_size is None:
        tile_size = settings.DEFAULT_TILE_SIZE

    driver = get_driver(settings.DRIVER_PATH, provider=settings.DRIVER_PROVIDER)

    with driver.connect():
        metadata = driver.get_metadata(keys)
        tile_data = xyz.get_tile_data(
            driver, keys, tile_xyz, tile_size=tile_size, preserve_values=preserve_values
        )

    if preserve_values:
        # bin output image into supplied labels, starting at 1
        colormap = cast(Mapping, colormap)

        labels, label_colors = list(colormap.keys()), list(colormap.values())

        cmap_or_palette = label_colors
        out = image.label(tile_data, labels)
    else:
        # determine stretch range from metadata and arguments
        stretch_range_ = list(metadata["range"])

        percentiles = metadata.get("percentiles", [])
        if stretch_min is not None:
            stretch_range_[0] = image.get_stretch_scale(stretch_min, percentiles)

        if stretch_max is not None:
            stretch_range_[1] = image.get_stretch_scale(stretch_max, percentiles)

        cmap_or_palette = cast(Optional[str], colormap)
        out = image.to_uint8(tile_data, *stretch_range_)

    return image.array_to_png(out, colormap=cmap_or_palette)


@trace("singleband_data_handler")
def singleband_data(
    keys: Union[Sequence[str], Mapping[str, str]], *, lon: float, lat: float
) -> Dict[str, Any]:
    """Return the singleband raster value at a geographic point."""
    settings = get_settings()
    driver = get_driver(settings.DRIVER_PATH, provider=settings.DRIVER_PROVIDER)

    with driver.connect():
        value = driver.get_raster_value(keys, coordinates=(lon, lat))

    if isinstance(keys, Mapping):
        ordered_keys = OrderedDict(
            (key_name, keys[key_name]) for key_name in driver.key_names
        )
    else:
        ordered_keys = OrderedDict(zip(driver.key_names, keys))

    return {
        "keys": ordered_keys,
        "coordinates": {"lon": lon, "lat": lat},
        "value": value,
    }
