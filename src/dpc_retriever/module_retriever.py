import os
import shutil
import time
import datetime
import requests
from filelock import FileLock

import numpy as np
import pandas as pd

import xarray as xr
import rioxarray
import geopandas as gpd

from .dpc.products import DPCProduct, DPCException
from .utils import filesystem, module_s3
from .cli.module_log import Logger




def retrieve_product(product: DPCProduct, date_time: datetime.datetime=None, max_retry: int = 3, retry_delay: int = 60) -> str:
    
    """
    Retrieve the product data for the specified date_time.
    
    :param product: The product to retrieve.
    :param date_time: The datetime of the data. If None, uses the last available datetime.
    :return: The path to the downloaded data file.
    """
    
    try:
        if not product.is_datetime_avaliable(date_time):
            raise DPCException(f"Product {product.code} not available for the specified date_time: {date_time}")
        
        data_filepath = product.download_data(
            date_time = date_time,
            out_dir = filesystem.tempdir()
        )
        
        if data_filepath is None or not os.path.exists(data_filepath):
            raise DPCException(f"Data for product {product.code} not available for the specified date_time: {date_time}")
    
    except Exception as e:
        if max_retry <= 0:
            raise DPCException(f"Failed to retrieve product {product.code} for date {date_time} after maximum retries ({max_retry}).")
        
        if type(e) is DPCException:
            Logger.debug(e.message)
        else:
            Logger.debug(f"Error retrieving product {product.code} for date_time {date_time}.")
            
        Logger.debug(f"Retrying in {retry_delay} seconds... (remaining retries: {max_retry})")
        
        time.sleep(retry_delay)
        return retrieve_product(product, date_time, max_retry-1, retry_delay)
    
    return data_filepath



def process_product(product: DPCProduct, data_filepath: str, date_time: datetime.datetime, bbox: tuple[float] | list[float], t_srs: str = None, out_format: str = None, output_dir: str = None) -> str:
    
    """
    Process the product data to the specified format and coordinate reference system.
    :param data_filepath: The path to the data file.
    :param bbox: The bounding box to clip the data, in the format (minx, miny, maxx, maxy).
    :param t_srs: The target spatial reference system to reproject the data to expected in EPSG format (e.g., 'EPSG:4326').
    :param out_format: The output format for the data file (e.g., '.tif', '.geotiff', '.nc', '.netcdf').
    :return: The path to the preprocessed data file.
    """
    
    data_type = None
    if filesystem.israster(data_filepath):
        data_type = 'raster'
    elif filesystem.isvector(data_filepath):
        data_type = 'vector'
    else:
        data_type = filesystem.justext(data_filepath)

    if data_type is None:
        raise DPCException(f"Error processing product {product.code} at {date_time}. Unsupported data type for file {data_filepath}. Must be raster or vector.")
    
    to_be_processed = any([
        bbox is not None,
        t_srs is not None,
        filesystem.justext(data_filepath) != out_format,
        data_type == 'raster',
        output_dir is not None
    ])
    
    dest_data_filepath = data_filepath    
    if output_dir is not None:
        dest_data_filepath = os.path.join(output_dir, module_s3.hive_path({'year': date_time.year, 'month': date_time.month, 'day': date_time.day, 'product': product.code}), filesystem.justfname(data_filepath))
        os.makedirs(os.path.dirname(dest_data_filepath), exist_ok=True)
    
    if data_type == 'raster':
        if data_filepath.endswith('.tif'):
            data = rioxarray.open_rasterio(data_filepath).to_dataset(name=product.code)
        else:
            data = xr.open_dataset(data_filepath)
        data[product.code] = xr.where(data[product.code] <= -9999, np.nan, data[product.code])
        data[product.code].rio.write_nodata(np.nan, inplace=True)
        if bbox is not None:
            data = data.rio.clip_box(*bbox)
        if t_srs is not None:
            data = data.rio.reproject(t_srs)
        if out_format is not None and filesystem.justext(data_filepath) != out_format:
            if out_format not in ['.tif', '.geotiff', '.nc', '.netcdf']:
                raise DPCException(f"Error processing product {product.code} at {date_time}. Unsupported output format {out_format} for raster data.")
            data_filepath = filesystem.forceext(data_filepath, out_format)
        if to_be_processed:
            if out_format in [None, '.tif', '.geotiff']:
                data[product.code].rio.to_raster(dest_data_filepath)
            elif out_format in ['.nc', '.netcdf']:
                data.to_netcdf(dest_data_filepath)
                
    elif data_type == 'vector':
        data = gpd.read_file(data_filepath)
        if bbox is not None:
            data = data.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]
        if t_srs is not None:
            data = data.to_crs(t_srs)
        if out_format is not None and filesystem.justext(data_filepath) != out_format:
            data_filepath = filesystem.forceext(data_filepath, out_format)
        if out_format is not None and out_format not in ['.shp', '.geojson']:
            raise DPCException(f"Error processing product {product.code} at {date_time}. Unsupported output format {out_format} for vector data.")
        if to_be_processed:
            data.to_file(dest_data_filepath)
            
    else:
        shutil.move(data_filepath, dest_data_filepath)
            
    return dest_data_filepath
            
        


def store_product(product: DPCProduct, data_filepath: str, date_time: datetime.datetime, s3_bucket: str, register_catalog: bool = True) -> bool:
    
    """
    Store the product data in the specified S3 bucket.
    
    :param product: The product to store.
    :param data_filepath: The path to the data file.
    :param date_time: The datetime of the data.
    :param s3_bucket: The S3 bucket to store the data in.
    :param register_avaliability: Whether to register the availability of the product.
    :return: True if the product was stored successfully, False otherwise.
    """
    
    hive_path = module_s3.hive_path({
        'year': date_time.year,
        'month': date_time.month,
        'day': date_time.day,
        'product': product.code
    })
    
    uri = f'{s3_bucket}/data/{hive_path}/{filesystem.justfname(data_filepath)}'
    upload_ok = module_s3.s3_upload(filename=data_filepath, uri=uri, remove_src=False)
    if filesystem.justext(data_filepath) == 'shp':
        additional_exts = ['.shx', '.dbf', '.prj', '.cpg']
        upload_ok = upload_ok and all([
            module_s3.s3_upload(
                filename = filesystem.forceext(data_filepath, additional_ext), 
                uri = filesystem.forceext(uri, additional_ext)
            )
            for additional_ext in additional_exts
        ])
    
    if not upload_ok:
        raise DPCException(f"Error storing product {product.code} at {date_time}. Failed to upload {data_filepath} to {uri}")
    
    if register_catalog:
        
        def catalog_object():
            return {
                'product': product.code,
                'date_time': date_time.isoformat(),
                'uri': uri
            }
            
        avaliability_uri = f'{s3_bucket}/catalog/{hive_path}/{product.code}.json'
        avaliable_filepath = filesystem.tempfilename(suffix='.json')
        
        with FileLock(filesystem.forceext(avaliable_filepath, 'lock')):
            _ = module_s3.s3_download(uri = avaliability_uri, fileout=avaliable_filepath)
            pd.DataFrame([catalog_object()]).to_json(avaliable_filepath, mode='a', orient='records', lines=True)
            upload_ok = module_s3.s3_upload(filename=avaliable_filepath, uri=avaliability_uri, remove_src=True)
            
            if not upload_ok:
                raise DPCException(f"Error processing product {product.code} at {date_time}. Failed to upload availability data to {avaliability_uri}")
            
    return uri