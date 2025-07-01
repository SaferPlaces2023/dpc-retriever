import os 
import glob
import shutil
import click

import pandas as pd
import geopandas as gpd

import logging
from logging import Logger

logger = logging.getLogger(__name__)

@click.command()
@click.option('--src', type=str, required=True, help='Source directory containing shapefiles to concatenate.')
@click.option('--prefix', type=str, default=None, help='Prefix to filter shapefiles by name.')
@click.option('--suffix', type=str, default=None, help='Suffix to filter shapefiles by name.')
@click.option('--contains', type=str, default=None, help='Substring to filter shapefiles by name.')
@click.option('--out', type=str, default=None, help='Output path for the concatenated shapefile. If not provided, defaults to a new shapefile in the source directory.')
@click.option('--remove_src', is_flag=True, default=False, help='If set, removes the source shapefiles after concatenation.')
@click.option('--debug', is_flag=True, default=False, help='Enable debug mode for detailed logging.')
def concat_shapefile(
    src: str,
    prefix: str | None = None,
    suffix: str | None = None,
    contains: str | None = None,
    out: str | None = None,
    remove_src: bool = False,
    
    debug: bool = False
):
    
    """ 
    Concatenate multiple shapefiles into a single shapefile.
    
    Examples:
    dpc-shp-concat --src ./output --prefix 01-07-2025 --debug --out ./output/01-07-2025.shp --remove_src 
    """
    
    if debug:
        logger.setLevel(logging.DEBUG)
    
    if not os.path.isdir(src):
        raise ValueError(f"Source path '{src}' is not a directory.")
    
    shapefiles = glob.glob(os.path.join(src, '**', '*.shp'), recursive=True)
    if prefix:
        shapefiles = [shp for shp in shapefiles if os.path.basename(shp).startswith(prefix)]
    if suffix:
        shapefiles = [shp for shp in shapefiles if os.path.basename(shp).endswith(suffix)]
    if contains:
        shapefiles = [shp for shp in shapefiles if contains in os.path.basename(shp)]
    
    if not shapefiles:
        logger.debug(f"No shapefiles found in '{src}'.")
        return
    
    gdfs = [ gpd.read_file(shp) for shp in shapefiles ]
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    logger.debug(f"Combining {len(gdfs)} shapefiles into one GeoDataFrame. Total records: {len(combined_gdf)}.")
    
    if out is None:
        out = os.path.join(src, src.strip('/').split('/')[-1] + '.shp')
        
    if remove_src:
        logger.debug(f"Removing source shapefiles from '{src}'.")
        for shp in shapefiles:
            add_ext = ['.shx', '.dbf', '.prj', '.cpg']
            os.remove(shp)
            for ext in add_ext:
                os.remove(shp.replace('.shp', ext))
            
    
    combined_gdf.to_file(out, driver='ESRI Shapefile')
    
    logger.debug(f"Combined shapefile saved to '{out}'.")
    
    return out