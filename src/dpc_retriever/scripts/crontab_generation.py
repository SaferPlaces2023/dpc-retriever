import os
import click
import logging
from logging import Logger

from ..dpc.products import _AVALIABLE_PRODUCTS

logger = logging.getLogger(__name__)


def freq2cron(freq: str) -> str:
    freq = freq.upper()

    if freq.endswith('T') or freq.endswith('MIN'):
        val = int(freq[:-1] if freq.endswith('T') else freq[:-3]) if freq[:-1] else 1
        return f"*/{val} * * * *"
    
    elif freq.endswith('H'):
        val = int(freq[:-1]) if freq[:-1] else 1
        return f"0 */{val} * * *"
    
    elif freq.endswith('D'):
        val = int(freq[:-1]) if freq[:-1] else 1
        return f"0 0 */{val} * *"
    
    elif freq.endswith('W'):
        val = int(freq[:-1]) if freq[:-1] else 1
        return f"0 0 * * */{val}"
    
    elif freq.endswith('M'): 
        val = int(freq[:-1]) if freq[:-1] else 1
        return f"0 0 1 */{val} *"
    
    else:
        raise ValueError(f"Unsupported frequency: {freq}")


@click.command()
@click.option('--products', type=str, multiple=True, default=None, help='List of product codes to include in the crontab. If not provided, all available products will be used.')
@click.option('--output_file', type=str, default='crontab.txt', help='Output file for the generated crontab.')
@click.option('--dt_strategy', type=click.Choice(['NOW','now', 'LAST','last']), default='NOW', help='Strategy for date time: NOW for current time, LAST for last available data.')
@click.option('--bbox', type=str, help='Bounding box in the format "minx,miny,maxx,maxy". If not provided, no bounding box will be applied.')
@click.option('--t_srs', type=str, help='Target spatial reference system in EPSG format (e.g., "EPSG:4326"). If not provided, original CRS will be used.')
@click.option('--output_dir', type=str, help='Directory where the output files will be saved. If not provided, current working directory will be used.')
@click.option('--s3_bucket', type=str, help='S3 bucket to copy the data to. If not provided, data will not be copied to S3.')
@click.option('--s3_catalog', is_flag=True, default=False, help='If set, the function will register the availability of the product in the S3 catalog file.')
@click.option('--max_retry', type=int, default=3, help='Maximum number of retries to attempt in case of failure. Default is 3.')
@click.option('--retry_delay', type=int, default=60, help='Delay in seconds between retries. Default is 60 seconds.')
@click.option('--debug', is_flag=True, default=False, help='Enable debug mode for detailed logging.')
def generate_crontab(
    products: list[str] | None = None,
    output_file: str = 'crontab.txt',
    
    dt_strategy: str | None = None,
    bbox: tuple[float] | list[float] | None = None,
    t_srs: str | None = None,
    output_dir: str | None = None,
    s3_bucket: str | None = None,
    s3_catalog: bool = False,
    max_retry: int = 3,
    retry_delay: int = 60,    
    
    debug: bool = False,
):
    """ 
    Generate a crontab file for scheduled retrieval of DPC products.
    
    Examples:
    dpc-crontab --output_file dpc-crontab.txt --dt_strategy now --output_dir ./output --debug   
    """
    
    
    if debug:
        logger.setLevel(logging.DEBUG)
        
    products = _AVALIABLE_PRODUCTS if products is None else [p for p in _AVALIABLE_PRODUCTS if p.code in products]

    if not products:
        products = _AVALIABLE_PRODUCTS
    
    if dt_strategy is not None and dt_strategy.upper() != 'NOW' and dt_strategy.upper() != 'LAST':
        raise ValueError("dt_strategy must be 'NOW' or 'LAST'.")
    if dt_strategy is None:
        dt_strategy = 'NOW'
    dt = None if dt_strategy.upper() == 'NOW' else 'LAST'

    script_name = 'dpc-retriever'
    
    cron_tasks = []
    
    for product in products:
        args = [
            '--product', product.code,
        ]
        if dt:
            args += [ '--dt', dt ]
        if bbox:
            args += [ '--bbox', ','.join(map(str, bbox)) ]
        if t_srs:
            args += [ '--t_srs', t_srs ]
        if output_dir:
            args += [ '--output_dir', output_dir ]
        if s3_bucket:
            args += [ '--s3_bucket', s3_bucket ]
        if s3_catalog:
            args += [ '--s3_catalog' ]
        args += [
            '--max_retry', str(max_retry),
            '--retry_delay', str(retry_delay)
        ]
        if debug:
            args += [ '--debug' ]
        
        cron_tasks.append((
            freq2cron(product.update_frequency), 
            args
        ))
        
    with open(output_file, 'w') as f:
        for freq,task in cron_tasks:
            f.write(f'{freq} {script_name} {" ".join(task)}\n')
            
    logger.debug(f"Crontab file '{output_file}' generated successfully with {len(cron_tasks)} tasks.")
    return output_file
        
    