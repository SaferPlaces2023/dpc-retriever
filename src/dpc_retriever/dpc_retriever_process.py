# =================================================================
#
# Authors: Tommaso Redaelli <tommaso.redaelli@gecosistema.com>
#
# Copyright (c) 2025 Tommaso Redaelli, Gecosistema srl
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import os
import json
import uuid
import datetime
import requests

import pandas as pd
import xarray as xr
import rioxarray

import gdal2numpy as g2n

from utils import module_s3, filesystem
from utils.status_exception import StatusException
from cli.module_log import Logger, set_log_debug
from dpc import products
from main import main_python

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError

# DOC: Not all input args of cli are implementaed... tryin to be specific and aligned with other retrieved process for SaferCast Project
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'arpav_retriever_process',
    'title': {
        'en': 'ARPAV Retriever Process',
    },
    'description': {
        'en': 'Process to retrieve data from the ARPAV seonsors.',
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'keywords': ['ARPAV', 'retriever', 'process', 'sensor', 'pygeoapi'],

    'inputs': {
        'token': {
            'title': 'secret token',
            'description': 'identify yourself',
            'schema': {
                'type': 'string'
            }
        },

        'lat_range': {
            'title': 'Latitude range',
            'description': 'The latitude range in format [lat_min, lat_max]. Values must be in EPSG:4326 crs. If no latitude range is provided, all latitudes will be returned',
            'schema': {
            }
        },
        'long_range': {
            'title': 'Longitude range',
            'description': 'The longitude range in format [long_min, long_max]. Values must be in EPSG:4326 crs. If no longitude range is provided, all longitudes will be returned',
            'schema': {
            }
        },
        'time_range': {
            'title': 'Time range',
            'description': 'The time range in format [time_start, time_end]. Both time_start and time_end must be in ISO-Format and related to at least one week ago. If no time range is provided, all times will be returned',
            'schema': {
            }
        },

        'product': {
            'title': 'Product',
            'description': 'The product code to retrieve.',
            'schema': {
                'type': 'string'
            }
        },

        'out': {
            'title': 'Output file path',
            'description': 'The output file path for the retrieved data. If neither out nor bucket_destination are provided, the output will be returned as a feature collection.',
            'schema': {
                'type': 'string'
            }
        },
        'out_format': {
            'title': 'Return format type',
            'description': 'The return format type. Possible values are "geojson" or "dataframe". "geojson" is default and preferable.',
            'schema': {
            }
        }, 
        'bucket_destination': {
            'title': 'Bucket destination',
            'description': 'The bucket destination where the data will be stored. If not provided, the data will not be stored in a bucket. If neither out nor bucket_destination are provided, the output will be returned as a feature collection.',
            'schema': {
                'type': 'string'
            }
        },

        'debug': {
            'title': 'Debug',
            'description': 'Enable Debug mode. Can be valued as true or false',
            'schema': {
            }
        }
    },

    'outputs': {
        'id': {
            'title': 'ID',
            'description': 'The ID of the process execution',
            'schema': {
            }
        },
    },

    'example': {
        "inputs": {
            'token': 'your_secret_token',
            'lat_range': [ 43.92, 44.77 ],
            'long_range': [ 12.20, 12.83 ],
            'time_range': ['2025-07-23T10:00:00', '2025-07-23T12:00:00'],
            'variable': 'SRI',
            'out': 'path/to/output/file.geojson',
            'out_format': 'geojson',
            'bucket_destination': 's3://your-bucket-name/store/data/prefix',
            'debug': True
        }
    }
}


class DPCRetrieverProcessor(BaseProcessor):
    """
    DPC Retriever Process for retrieving data from DPC REST API.
    """

    _tmp_data_folder = os.path.join(os.getcwd(), 'DPCRetrieverProcess')

    def __init__(self, processor_def):
        """
        Initialize the DPC Retriever Process.
        """
        super().__init__(processor_def, PROCESS_METADATA)

        if not os.path.exists(self._tmp_data_folder):
            os.makedirs(self._tmp_data_folder, exist_ok=True)


    def argument_validation(self, data):
        """
        Validate the arguments passed to the processor.
        """

        token = data.get('token', None)
        debug = data.get('debug', False)

        if token is None or token != os.getenv("INT_API_TOKEN", "token"):
            raise StatusException(StatusException.DENIED, 'ACCESS DENIED: wrong token')
            
        if type(debug) is not bool:
            raise StatusException(StatusException.INVALID, 'debug must be a boolean')
        if debug:
            set_log_debug() 

        product = data.get('product', None)
        lat_range = data.get('lat_range', None)
        long_range = data.get('long_range', None)
        time_range = data.get('time_range', None)
        time_start = time_range[0] if type(time_range) in [list, tuple] else time_range
        time_end = time_range[1] if type(time_range) in [list, tuple] else None
        out_format = data.get('out_format', None)
        bucket_destination = data.get('bucket_destination', None)
        out = data.get('out', None)

        if product is None:
            raise StatusException(StatusException.INVALID, 'product must be provided')
        if not isinstance(product, str):
            raise StatusException(StatusException.INVALID, 'product must be a string')
        product = products.product_by_code(product)
        if product is None:
            raise StatusException(StatusException.INVALID, f'product {product} not found')

        if lat_range is not None:
            if type(lat_range) is not list or len(lat_range) != 2:
                raise StatusException(StatusException.INVALID, 'lat_range must be a list of 2 elements')
            if type(lat_range[0]) not in [int, float] or type(lat_range[1]) not in [int, float]:
                raise StatusException(StatusException.INVALID, 'lat_range elements must be float')
            if lat_range[0] < -90 or lat_range[0] > 90 or lat_range[1] < -90 or lat_range[1] > 90:
                raise StatusException(StatusException.INVALID, 'lat_range elements must be in the range [-90, 90]')
            if lat_range[0] > lat_range[1]:
                raise StatusException(StatusException.INVALID, 'lat_range[0] must be less than lat_range[1]')
        
        if long_range is not None:
            if type(long_range) is not list or len(long_range) != 2:
                raise StatusException(StatusException.INVALID, 'long_range must be a list of 2 elements')
            if type(long_range[0]) not in [int, float] or type(long_range[1]) not in [int, float]:
                raise StatusException(StatusException.INVALID, 'long_range elements must be float')
            if long_range[0] < -180 or long_range[0] > 180 or long_range[1] < -180 or long_range[1] > 180:
                raise StatusException(StatusException.INVALID, 'long_range elements must be in the range [-180, 180]')
            if long_range[0] > long_range[1]:
                raise StatusException(StatusException.INVALID, 'long_range[0] must be less than long_range[1]')
        
        if time_start is None:
            raise StatusException(StatusException.INVALID, 'Cannot process without a time valued')
        if type(time_start) is not str:
            raise StatusException(StatusException.INVALID, 'time_start must be a string')
        if type(time_start) is str:
            try:
                time_start = datetime.datetime.fromisoformat(time_start)
            except ValueError:
                raise StatusException(StatusException.INVALID, 'time_start must be a valid datetime iso-format string')
        
        if time_end is not None:
            if type(time_end) is not str:
                raise StatusException(StatusException.INVALID, 'time_end must be a string')
            if type(time_end) is str:
                try:
                    time_end = datetime.datetime.fromisoformat(time_end)
                except ValueError:
                    raise StatusException(StatusException.INVALID, 'time_end must be a valid datetime iso-format string')
            if time_start > time_end:
                raise StatusException(StatusException.INVALID, 'time_start must be less than time_end')
            
        time_start = time_start.replace(minute=(time_start.minute // 5) * 5, second=0, microsecond=0)
        time_end = time_end.replace(minute=(time_end.minute // 5) * 5, second=0, microsecond=0) if time_end is not None else time_start + datetime.timedelta(hours=1)
        if time_end < (datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(hours=48)).replace(tzinfo=None):
            raise StatusException(StatusException.INVALID, 'Time range must be within the last 48 hours')

        if out_format is not None:  
            if type(out_format) is not str:
                raise StatusException(StatusException.INVALID, 'out_format must be a string or null')
            if out_format not in ['geojson']:
                raise StatusException(StatusException.INVALID, 'out_format must be one of ["geojson"]')
        else:
            out_format = 'geojson'
        
        if bucket_destination is not None:
            if type(bucket_destination) is not str:
                raise StatusException(StatusException.INVALID, 'bucket_destination must be a string')
            if not bucket_destination.startswith('s3://'):
                raise StatusException(StatusException.INVALID, 'bucket_destination must start with "s3://"')
            
        if out is not None:
            if type(out) is not str:
                raise StatusException(StatusException.INVALID, 'out must be a string')
            if not out.endswith('.geojson'):
                raise StatusException(StatusException.INVALID, 'out must end with ".geojson"')
            dirname, _ = os.path.split(out)
            if dirname != '' and not os.path.exists(dirname):
                os.makedirs(dirname)

        return {
            'product': product,
            'lat_range': lat_range,
            'long_range': long_range,
            'time_start': time_start,
            'time_end': time_end,
            'out_format': out_format,
            'bucket_destination': bucket_destination,
            'out': out
        }
        

    def retrieve_data(self, product, lat_range, long_range, time_start, time_end, debug):
        output_datetimes = pd.date_range(start=time_start, end=time_end, freq=product.update_frequency).to_list()
        output_filenames = []
        
        for dt in output_datetimes:
            output_dt_obj = main_python(
                product = product.code,
                dt = dt,
                bbox = [ long_range[0], lat_range[0], long_range[1], lat_range[1] ],
                
                t_srs = None,
                out_format = None,
                output_dir = self._tmp_data_folder,
                s3_bucket = None,
                s3_catalog = False,
                max_retry = 0,
                retry_delay = 0,
                backend = None,
                jid = None,
                version = False,
                
                debug = debug
            )
            output_dt_filename = output_dt_obj['body']['data']['filename']
            output_filenames.append(output_dt_filename)
        
        return output_datetimes, output_filenames
    

    def build_dataset(self, product, data_datetimes, data_filenames):
        # DOC: Concat along time dimension
        dataarrays = [ rioxarray.open_rasterio(filename) for filename in data_filenames ]
        dataarray = xr.concat(dataarrays, dim='time')
        dataset = dataarray.to_dataset(name=product.code)
        dataset['time'] = xr.DataArray(data_datetimes, dims='time', coords={'time': data_datetimes})
        # DOC: Remove useless band dimension
        dataset = dataset.drop_vars('band')
        dataset[product.code] = (('time', 'y','x'), dataset[product.code].data[:,0,:,:])
        return dataset        


    def create_timestamp_raster(self, product, dataset, out):
        timestamps = [datetime.datetime.fromisoformat(str(ts).replace('.000000000','')) for ts in dataset.time.values]
        
        if out is None:
            merged_raster_filename = f'DPC/{product.code}/DPC__{product.code}__{timestamps[-1]}.tif'
            merged_raster_filepath = os.path.join(self._tmp_data_folder, merged_raster_filename)
        else:
            merged_raster_filepath = out
        
        xmin, xmax = dataset.lon.min().item(), dataset.lon.max().item()
        ymin, ymax = dataset.lat.min().item(), dataset.lat.max().item()
        nx, ny = dataset.dims['lon'], dataset.dims['lat']
        pixel_size_x = (xmax - xmin) / nx
        pixel_size_y = (ymax - ymin) / ny

        data = dataset.sortby('lat', ascending=False)[self.variable_name].values
        geotransform = (xmin, pixel_size_x, 0, ymax, 0, -pixel_size_y)
        projection = dataset.attrs.get('crs', 'EPSG:4326')
        
        g2n.Numpy2GTiffMultiBanda(
            data,
            geotransform,
            projection,
            merged_raster_filepath,
            format="COG",
            save_nodata_as=-9999.0,
            metadata={
                'band_names': [ts.isoformat() for ts in timestamps],
                'type': product.measure_type,
                'unit': product.measure_unit
            }
        )
    
        return merged_raster_filepath


    def execute(self, data):

        mimetype = 'application/json'

        outputs = {}

        try:
            # DOC: Args validation
            args = self.argument_validation(data)
            Logger.debug(f'Validated process parameters')

            # DOC: Call main retriever function
            out_datetimes, out_filenames = self.retrieve_data(
                product = args['product'],
                lat_range = args['lat_range'],
                long_range = args['long_range'],
                time_start = args['time_start'],
                time_end = args['time_end'],
                debug = data.get('debug', False)
            )

            # DOC: Build dataset
            dataset = self.build_dataset(
                product = args['product'],
                data_datetimes = out_datetimes,
                data_filenames = out_filenames
            )

            # DOC: Create timestamp raster
            timestamp_raster = self.create_timestamp_raster(
                product = args['product'],
                dataset = dataset,
                out = args['out'],
            )
            
            # DOC: Store data in bucket if bucket_destination is provided
            if args['bucket_destination'] is not None:
                bucket_uris = []
                bucket_uri = f"{args['bucket_destination']}/{filesystem.justfname(timestamp_raster)}"
                upload_status = module_s3.s3_upload(timestamp_raster, bucket_uri)
                if not upload_status:
                    raise StatusException(StatusException.ERROR, f"Failed to upload data to bucket {args['bucket_destination']}")
                bucket_uris.append(bucket_uri)
                Logger.debug(f"Data stored in bucket: {bucket_uri}")
                
            # DOC: Prepare outputs
            if args['bucket_destination'] is not None or args['out'] is not None:
                outputs = { 'status': 'OK' }
                if args['bucket_destination'] is not None:
                    outputs = {
                        ** outputs,
                        ** ( {'uri': bucket_uris[0]} if len(bucket_uris) == 1 else {'uris': bucket_uris} )
                    }
                if args['out'] is not None:
                    outputs = {
                        ** outputs,
                        ** {'filepath': timestamp_raster}
                    }
            else:
                outputs = timestamp_raster
    
        except StatusException as err:
            outputs = {
                'status': err.status,
                'message': str(err)
            }
        except Exception as err:
            outputs = {
                'status': StatusException.ERROR,
                'error': str(err)
            }
            raise ProcessorExecuteError(str(err))
        finally:
            filesystem.garbage_folders(self._tmp_data_folder)
            Logger.debug(f'Cleaned up temporary data folder: {self._tmp_data_folder}')
        
        return mimetype, outputs
    
    def __repr__(self):
        return f'<DPCRetrieverProcess> {self.name}'