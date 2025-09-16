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
import sys
import click
import traceback
import pprint
import json

from .utils.filesystem import clean_temp_files
from .utils.module_s3 import copy
from .utils.module_prologo import prologo, epilogo
from .utils.module_status import set_status
from .cli.module_log import Logger, logging
from .dpc import products
from . import module_args, module_retriever


@click.command()
# -----------------------------------------------------------------------------
# Specific options of your CLI application
# -----------------------------------------------------------------------------

@click.option('--product', type=click.STRING, required=False, default=None,
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
@click.option('--output_dir', type=click.STRING, required=False, default=None,
              help="The directory where the output file will be saved. If not provided, the file will be saved in the current working directory.")
@click.option('--s3_bucket', type=click.STRING, required=False, default=None,
                help="The S3 bucket to copy the data to. If not provided, the data will not be copied to S3.")
@click.option('--s3_catalog', is_flag=True, required=False, default=False,
              help="If set, the function will register the availability of the product in the S3 catalog file")
@click.option('--max_retry', type=click.INT, required=False, default=3,
              help="The maximum number of retries to attempt in case of failure. Default is 3.")
@click.option('--retry_delay', type=click.INT, required=False, default=60,
              help="The delay in seconds between retries. Default is 60 seconds.")
@click.option('--status', is_flag=True, required=False, default=False,
              help="If set, the function will list status of available products and exit without performing any retrieval. This is useful for checking available products before making a request. If used in combinationwith --product, it will list the details of the specified product. If used in combination with --verbose, it will print the details of all available products.")

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
    dpc-retriever --product SRI --dt last --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog
    dpc-retriever --product SRI --dt 2025-06-30T10:55:00 --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog --max_retry 5 --retry_delay 10
    dpc-retriever --product SRI --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --output_dir ./outputs --max_retry 5 --retry_delay 10
    
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
    output_dir = None,
    s3_bucket = None,
    s3_catalog = False,
    max_retry = None,
    retry_delay = None,
    
    status = False,
    
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
        
        if status:
            if product is not None:
                if products.product_by_code(product) is None:
                    raise ValueError(f"Product '{product}' not found. Use --list_products to see available products.")
            list_products = products._ALL_PRODUCTS if product is None else [products.product_by_code(product)]
            if verbose:
                out = [
                    p.to_dict(description=True, last_avaliable_datetime=True) for p in list_products
                ]
            else:
                out = [p.code for p in list_products if p.code in list(map(lambda x: x.code, products.avaliable_products()))]
                if product is not None:
                    out = product in out
            print(json.dumps(out, indent=2))
            sys.exit(0)
            
            
                

        # DOC: -- Arguments validation ---------------------------------------------
        kwargs = {
            'product': product,
            'dt': dt,
            'bbox': bbox,
            't_srs': t_srs,
            'out_format': out_format,
            'return_data': return_data,
            'output_dir': output_dir,
            's3_bucket': s3_bucket,
            's3_catalog': s3_catalog,
            'max_retry': max_retry,
            'retry_delay': retry_delay
        }
        product, dt, bbox, t_srs, out_format, return_data, output_dir, s3_bucket, s3_catalog, max_retry, retry_delay = module_args.args_validation(** kwargs)
        Logger.debug(f"Validated arguments: {kwargs}")
        
        set_status(backend, jid, 10, "Arguments validated successfully.")
        
        # DOC: -- Main logic. Do work here -----------------------------------------
        
        product_file = module_retriever.retrieve_product(
            product = product,
            date_time = dt,
            max_retry = max_retry,
            retry_delay = retry_delay
        )
        
        set_status(backend, jid, 40, f"Product retrieved successfully: {product_file}")
        
        product_file = module_retriever.process_product(
            product = product,
            data_filepath = product_file,
            date_time = dt,
            bbox = bbox,
            t_srs = t_srs,
            out_format = out_format,
            output_dir = output_dir
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
        else:
            output['data'] = { 'filename': product_file }
            if product_uri is not None:
                output['data']['uri'] = product_uri
        
        
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

    finally:
        # DOC: -- Cleanup the temporary files of this run --------------------------
        clean_temp_files(from_garbage_collection=True)
        
    # DOC: -- Cleanup the temporary files if needed --------------------------------
    epilogo(t0, backend, jid)
    
    return result
