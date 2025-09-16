import os
import re
import zipfile
import requests
import datetime
import warnings
import logging

from enum import Enum

import numpy as np 
import pandas as pd
import xarray as xr
import rioxarray

import geopandas as gpd



logging.getLogger("urllib3.connection").setLevel(logging.ERROR) # DOC: (Suppress urllib3 connection warnings) IGNORE HeaderParsingError(defects=defects, unparsed_data=unparsed_data)



class DPCException(Exception):
    """Custom exception for DPC retriever errors."""
    
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"DPCException: {self.message}"


class DPCProduct():
    
    base_url = 'https://radar-api.protezionecivile.it/wide/product'
    
    def __init__(self, code, name, description, update_frequency, measure_type=None, measure_unit=None):
        self.code = code
        self.name = name
        self.description = description
        self.update_frequency = update_frequency
        self.measure_type = measure_type
        self.measure_unit = measure_unit
        
    
    def to_dict(self, description=False, last_avaliable_datetime=False):
        """
        Returns a dictionary representation of the product.
        """
        last_avaliable_datetime_dict = dict()
        if last_avaliable_datetime:
            try: 
                last_avaliable_datetime_dict['last_avaliable_datetime'] = self.last_avaliable_datetime().isoformat()
            except Exception as e:
                last_avaliable_datetime_dict['last_avaliable_datetime'] = None
        description_dict = { 'description': self.description } if description else dict()
        return {
            'code': self.code,
            'name': self.name,
            ** description_dict,
            'update_frequency': self.update_frequency,
            ** last_avaliable_datetime_dict
        }
    
    
    def now_datetime(self):
        """
        Returns the current datetime in UTC.
        """
        now_dt = datetime.datetime.now(tz=datetime.timezone.utc)
        return pd.Timestamp(now_dt).floor(self.update_frequency).to_pydatetime()
    
    
    def is_datetime_avaliable(self, date_time):
        url = f"{self.base_url}/existsProduct"
        params = {
            'type': self.code,
            'time': str(int(date_time.timestamp() * 1000))  # Convert datetime to milliseconds
        }
        response = requests.get(url = url, params = params)
        if response.status_code == 200: 
            return response.json()
        else:
            return False
        
    
    def last_avaliable_datetime(self):
        url = f"{self.base_url}/findLastProductByType"
        params = { "type": self.code }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            out = response.json()
            last_avaliable = out.get('lastProducts', [])
        else:
            raise DPCException(f"Error fetching last available product for {self.code}: {response.status_code} - {response.text}")
        
        avaliable_details = [la for la in last_avaliable if la.get('productType') == self.code]
        if avaliable_details:
            last_avaliable_time = avaliable_details[0]['time']
            last_avaliable_datetime = datetime.datetime.fromtimestamp(last_avaliable_time // 1000, tz=datetime.timezone.utc)
            return last_avaliable_datetime
        else:
            raise DPCException(f"No available details found for product type {self.code}")
           
        
    def request_data(self, date_time=None):
        """
        Returns the last available data for the product.
        """
        
        if not self.is_datetime_avaliable(date_time):
            raise DPCException(f"Product {self.code} not available for the specified date_time: {date_time}")
        
        date_time = self.last_avaliable_datetime() if date_time is None else date_time
        if date_time is None:
            return None
        
        url = f"{self.base_url}/downloadProduct"
        json_params = {
            "productType": self.code,
            "productDate": str(int(date_time.timestamp() * 1000))
        }
        
        response = requests.post(url, json=json_params)
        
        if response.status_code == 200:
            return response
        else:
            raise DPCException(f"Error fetching product data for {self.code}: {response.status_code} - {response.text}")
        
        
    def download_data(self, date_time = None, out_dir='.', return_data=False) -> None | str | gpd.GeoDataFrame | xr.Dataset:
        """
        Downloads the product data for the specified date_time.
        If date_time is None, it uses the last available datetime.
        If output_file is None, it saves the file with a default name.
        """
        
        def get_attachment_filename(response):
            """
            Extracts the filename from the Content-Disposition header.
            """
            rgx_fn = re.compile(r'filename="([^"]+)"')
            filename_match = rgx_fn.findall(response.headers.get('Content-Disposition', ''))
            return filename_match[0] if filename_match else None
        
        date_time = self.last_avaliable_datetime() if date_time is None else date_time
        response = self.request_data(date_time = date_time)
        
        if response.status_code == 200:
            
            attachment_filename = get_attachment_filename(response)
            if attachment_filename is None:
                raise DPCException(f"Could not extract filename from response headers for product {self.code}.")

            output_file = os.path.join(out_dir, attachment_filename)
            with open(output_file, 'wb') as f:
                f.write(response.content)
                
            if output_file.endswith('.zip'):
                with zipfile.ZipFile(output_file, 'r') as zip_ref:
                    extracted_dir = os.path.join(out_dir, attachment_filename.replace('.zip', ''))
                    zip_ref.extractall(extracted_dir)
                output_file = os.path.join(extracted_dir, f"{date_time.strftime('%d-%m-%Y-%H-%M')}.shp")
                ds = gpd.read_file(output_file)
            
            elif output_file.endswith('.tif'):
                ds = rioxarray.open_rasterio(output_file).to_dataset(name=self.code)
                ds = ds.rename({'band': 'time'})
                ds['time'] = [ date_time ]
                ds['x'] = ds.x.values.astype(np.float32)
                ds['y'] = ds.y.values.astype(np.float32)
                ds[self.code] = xr.where(ds[self.code] == -9999, np.nan, ds[self.code])
            
            return ds if return_data else output_file
            
        else:
            raise DPCException(f"Error downloading product data for {self.code}: {response.status_code} - {response.text}")