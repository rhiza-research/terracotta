import os

import pytest

import numpy as np
import rasterio


def pytest_configure(config):
    os.environ['TC_TESTING'] = '1'


def pytest_unconfigure(config):
    os.environ['TC_TESTING'] = '0'


@pytest.fixture(scope='session')
def raster_file(tmpdir_factory):
    import affine

    raster_data = np.random.randint(0, np.iinfo(np.uint16).max, size=(256, 256), dtype='uint16')
    profile = {
        'driver': 'GTiff',
        'dtype': 'uint16',
        'nodata': 0,
        'width': raster_data.shape[1],
        'height': raster_data.shape[0],
        'count': 1,
        'crs': {'init': 'epsg:32637'},
        'transform': affine.Affine(
            2.0, 0.0, 694920.0,
            0.0, -2.0, 2055666.0
        )
    }

    outpath = tmpdir_factory.mktemp('raster').join('img.tif')
    with rasterio.open(str(outpath), 'w', **profile) as dst:
        dst.write(raster_data, 1)

    return outpath


@pytest.fixture(scope='session')
def big_raster_file(tmpdir_factory):
    import affine

    raster_data = np.random.randint(0, np.iinfo(np.uint16).max, size=(1024, 1024), dtype='uint16')
    profile = {
        'driver': 'GTiff',
        'dtype': 'uint16',
        'nodata': 0,
        'width': raster_data.shape[1],
        'height': raster_data.shape[0],
        'count': 1,
        'crs': {'init': 'epsg:32637'},
        'transform': affine.Affine(
            2.0, 0.0, 694920.0,
            0.0, -2.0, 2055666.0
        )
    }

    outpath = tmpdir_factory.mktemp('raster').join('img.tif')
    with rasterio.open(str(outpath), 'w', **profile) as dst:
        dst.write(raster_data, 1)

    return outpath


@pytest.fixture(scope='session')
def invalid_raster_file(tmpdir_factory):
    """A raster file that is all nodata"""
    import affine

    raster_data = np.full((256, 256), 0, dtype='uint16')
    profile = {
        'driver': 'GTiff',
        'dtype': 'uint16',
        'nodata': 0,
        'width': raster_data.shape[1],
        'height': raster_data.shape[0],
        'count': 1,
        'crs': {'init': 'epsg:32637'},
        'transform': affine.Affine(
            2.0, 0.0, 694920.0,
            0.0, -2.0, 2055666.0
        )
    }

    outpath = tmpdir_factory.mktemp('raster').join('img.tif')
    with rasterio.open(str(outpath), 'w', **profile) as dst:
        dst.write(raster_data, 1)

    return outpath


@pytest.fixture(scope='session')
def raster_file_xyz(raster_file):
    import rasterio
    import rasterio.warp
    import mercantile

    with rasterio.open(str(raster_file)) as src:
        raster_bounds = rasterio.warp.transform_bounds(src.crs, 'epsg:4326', *src.bounds)
    raster_center_x = (raster_bounds[0] + raster_bounds[2]) / 2
    raster_center_y = (raster_bounds[1] + raster_bounds[3]) / 2

    zoom = 12
    tile = mercantile.tile(raster_center_x, raster_center_y, zoom)
    return (tile.x, tile.y, zoom)


@pytest.fixture(scope='session')
def raster_file_xyz_lowzoom(raster_file):
    import rasterio
    import rasterio.warp
    import mercantile

    with rasterio.open(str(raster_file)) as src:
        raster_bounds = rasterio.warp.transform_bounds(src.crs, 'epsg:4326', *src.bounds)
    raster_center_x = (raster_bounds[0] + raster_bounds[2]) / 2
    raster_center_y = (raster_bounds[1] + raster_bounds[3]) / 2

    zoom = 10
    tile = mercantile.tile(raster_center_x, raster_center_y, zoom)
    return (tile.x, tile.y, zoom)


@pytest.fixture(scope='session')
def read_only_database(raster_file, tmpdir_factory):
    from terracotta import get_driver

    keys = ('key1', 'key2')

    dbpath = tmpdir_factory.mktemp('db').join('db-readonly.sqlite')
    driver = get_driver(dbpath, provider='sqlite')
    with driver.connect():
        driver.create(keys)
        driver.insert(('val11', 'val12'), str(raster_file), ['extra_data'])
        driver.insert(('val21', 'val22'), str(raster_file))
        driver.insert(('val21', 'val23'), str(raster_file))
        driver.insert(('val21', 'val24'), str(raster_file))

    return dbpath


@pytest.fixture()
def use_read_only_database(read_only_database, monkeypatch):
    import terracotta
    settings = terracotta.config.parse_config({'DRIVER_PATH': str(read_only_database)})
    with monkeypatch.context() as m:
        m.setattr(terracotta, 'get_settings', lambda: settings)
        yield
