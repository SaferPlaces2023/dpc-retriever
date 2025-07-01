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
# Name:        main.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     18/03/2021
# -----------------------------------------------------------------------------
import click
import traceback
import pprint

from .utils.module_s3 import copy
from .utils.module_prologo import prologo, epilogo
from .utils.module_status import set_status
from .cli.module_log import Logger
from . import module_args, module_retriever


@click.command()
# -----------------------------------------------------------------------------
# Specific options of your CLI application
# -----------------------------------------------------------------------------

@click.option('--product', type=click.STRING, required=True, default=None,
              help="The product code to retrieve.")
@click.option('--dt', type=click.STRING, required=False, default=None,
              help="The date and time of the product to retrieve in ISO format (YYYY-MM-DDTHH:MM:SS). If not provided, the last available product will be retrieved.")
@click.option('--bbox', type=click.STRING, required=False, default=None,
                help="The bounding box to clip the data, in the format 'minx,miny,maxx,maxy'. If not provided, the entire product will be retrieved.")
@click.option('--t_srs', type=click.STRING, required=False, default=None,
                help="The target spatial reference system to reproject the data to, expected in EPSG format (e.g., 'EPSG:4326'). If not provided, the original CRS will be used.")
@click.option('--out_format', type=click.STRING, required=False, default=None,
                help="The output format for the data file (e.g., '.tif', '.geotiff', '.nc', '.netcdf'). If not provided, the original format will be used.")
@click.option('--return_data', is_flag=True, required=False, default=False,
              help="If set, the function will return the data as a byte stringinstead of file reference")
@click.option('--s3_bucket', type=click.STRING, required=False, default=None,
                help="The S3 bucket to copy the data to. If not provided, the data will not be copied to S3.")
@click.option('--s3_catalog', is_flag=True, required=False, default=False,
              help="If set, the function will register the availability of the product in the S3 catalog file")

# -----------------------------------------------------------------------------
# Common options to all Gecosistema CLI applications
# -----------------------------------------------------------------------------
@click.option('--backend', type=click.STRING, required=False, default=None,
              help="The backend to use for sending back progress status updates to the backend server.")
@click.option('--jid', type=click.STRING, required=False, default=None,
              help="The job ID to use for sending back progress status updates to the backend server. If not provided, it will be generated automatically.")
@click.option('--version', is_flag=True, required=False, default=False,
              help="Show the version of the package.")
@click.option('--debug', is_flag=True, required=False, default=False,
              help="Debug mode.")
@click.option('--verbose', is_flag=True, required=False, default=False,
              help="Print some words more about what is doing.")
def main_click(**kwargs):
    """
    DPC Retriever - Command Line Interface
    
    Some example usage:
    dpc-retriever --product SRI  --bbox 12,45.15,12.7,45.6 --t_srs 'EPSG:4326' --out_format '.tif' --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog
    
    """
    output = main_python(**kwargs)
    
    Logger.debug(pprint.pformat(output))
    
    return output


def main_python(
    # --- Specific options ---
    
    product = None,
    dt = None,
    bbox = None,
    t_srs = None,
    out_format = None,
    return_data = False,
    s3_bucket = None,
    s3_catalog = False,
    
    # --- Common options ---
    
    backend = None,
    jid = None,
    version = False,
    debug = False,
    verbose = False
):
    """
    main_python - main function
    """
    
    try:
    
        # DOC: -- Init logger + cli settings + handle version and debug ------------
        t0, jid = prologo(backend, jid, version, verbose, debug)

        # DOC: -- Arguments validation ---------------------------------------------
        kwargs = {
            'product': product,
            'dt': dt,
            'bbox': bbox,
            't_srs': t_srs,
            'out_format': out_format,
            'return_data': return_data,
            's3_bucket': s3_bucket,
            's3_catalog': s3_catalog
        }
        product, dt, bbox, t_srs, out_format, return_data, s3_bucket, s3_catalog = module_args.args_validation(** kwargs)
        Logger.debug(f"Validated arguments: {kwargs}")
        
        set_status(backend, jid, 10, "Arguments validated successfully.")
        
        # DOC: -- Main logic. Do work here -----------------------------------------
        
        product_file = module_retriever.retrieve_product(
            product = product,
            date_time = dt
        )
        
        set_status(backend, jid, 40, f"Product retrieved successfully: {product_file}")
        
        product_file = module_retriever.process_product(
            product = product,
            data_filepath = product_file,
            bbox = bbox,
            t_srs = t_srs,
            out_format = out_format
        )
        
        set_status(backend, jid, 70, f"Product preprocessed successfully: {product_file}")
        
        product_uri = None
        if s3_bucket is not None:
            product_uri = module_retriever.store_product(
                product = product,
                data_filepath = product_file,
                date_time = dt,
                s3_bucket = s3_bucket,
                register_catalog = s3_catalog
            )
            
            set_status(backend, jid, 90, f"Product stored in S3 successfully: {product_uri}")
        
        output = dict()
        if return_data:
            with open(product_file, 'rb') as f:
                output['data'] = f.read()
        elif product_uri is not None:
            output['data'] = product_uri
        else:
            output['data'] = product_file
        
        
        # DOC: -- Return the response ----------------------------------------------
        result = {
            "status": "OK",
            "body": output
        }
        
    except Exception as e:
        result = {
            "status": "ERROR",
            "body": {
                "error": str(e),
                ** ({"traceback": traceback.format_exc()} if debug else dict())
            }
        }
        
    # DOC: -- Cleanup the temporary files if needed ----------------------------
    epilogo(t0, backend, jid)
    
    return result
