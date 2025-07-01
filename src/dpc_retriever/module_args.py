# -----------------------------------------------------------------------------
# License:
# Copyright (c) 2025 Gecosistema S.r.l.
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
#
# Name:        module_args.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     25/06/2025
# -----------------------------------------------------------------------------
import os 
import datetime

from .cli.module_log import Logger
from .utils import module_s3
from .dpc import products


def args_validation(**kwargs):
    """
    Check if the provided arguments are valid.
    :param args: List of arguments to check.
    :return: True if all arguments are valid, False otherwise.
    """
    
    product = kwargs.get('product', None)
    if product is None or not isinstance(product, str):
        raise ValueError("Product must be a non-empty string.")
    else:
        product = products.product_by_code(product)
        if product is None:
            raise ValueError(f"Product '{kwargs['product']}' not found. Please check the product code.")
    
    dt = kwargs.get('dt', None)
    if dt is not None:
        try:
            dt = datetime.datetime.fromisoformat(dt)
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
    else:
        dt = product.last_avaliable_datetime()
        if dt is None:
            raise ValueError(f"No available data for product '{product.code}'. Please provide a valid date or check the product availability.")
    
    bbox = kwargs.get('bbox', None)
    if bbox is not None:
        if isinstance(bbox, str):
            try:
                bbox = [float(coord) for coord in bbox.split(',')]
            except ValueError:
                raise ValueError("Bounding box must be a string of four comma-separated floats (minx,miny,maxx,maxy).")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError("Bounding box must be a list or tuple of four floats (minx, miny, maxx, maxy).")
        if any(not isinstance(coord, (int, float)) for coord in bbox):
            raise ValueError("Bounding box coordinates must be numeric (int or float).")
    
    t_srs = kwargs.get('t_srs', None)
    if t_srs is not None:
        if not isinstance(t_srs, str) or not t_srs.startswith('EPSG:'):
            raise ValueError("Target spatial reference system must be a string starting with 'EPSG:'.")
        
    out_format = kwargs.get('out_format', None)
    if out_format is not None:
        if not isinstance(out_format, str) or not out_format.startswith('.'):
            raise ValueError("Output format must be a string starting with '.' (e.g., '.tif', '.geotiff', '.nc', '.netcdf').")
        if not any(out_format.endswith(of) for of in ['tif', 'geotiff', 'nc', 'netcdf', 'geojson', 'shp']):
            raise ValueError("Unsupported output format. Supported formats are: .tif, .geotiff, .nc, .netcdf, json, geojson, shp.")
        
    return_data = kwargs.get('return_data', False)
    if not isinstance(return_data, bool):
        raise ValueError("Return data must be a boolean value (True or False).")

    s3_bucket = kwargs.get('s3_bucket', None)
    if s3_bucket is not None and not module_s3.iss3(s3_bucket):
        raise ValueError("S3 bucket must be a valid S3 path (e.g., 's3://bucket-name/').")
    
    s3_catalog = kwargs.get('s3_catalog', False)
    if not isinstance(s3_catalog, bool):
        raise ValueError("S3 registration flag must be a boolean value (True or False).")
    if s3_bucket is None and s3_catalog:
        raise ValueError("S3 registration cannot be enabled without providing an S3 bucket.")
    
    return product, dt, bbox, t_srs, out_format, return_data, s3_bucket, s3_catalog