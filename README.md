# dpc-retriever

**dpc-retriever** is a package built to get data from DPC service api

### DPC documentation:
- https://dpc-radar.readthedocs.io/it/latest/index.html
- https://dpc-radar.readthedocs.io/it/latest/api.html

### Installation

Different option based on py version: *__py311__* / *__py312__* / *__py313__* 

#### With pip
- `pip install "git+https://github.com/SaferPlaces2023/dpc-retriever.git#egg=dpc-retriever[py***]"`

#### As dependency
- `dpc-retriever[py***] @ git+https://github.com/SaferPlaces2023/dpc-retriever.git`


### Scripts:

#### dpc-retriever
- `dpc-retriever --help`
- `dpc-retriever --status --verbose`
- `dpc-retriever --product SRI --dt last --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog`
- `dpc-retriever --product SRI --dt 2025-06-30T10:55:00 --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog --max_retry 5 --retry_delay 10`
- `dpc-retriever --product SRI --bbox 12,45.15,12.7,45.6 --t_srs EPSG:4326 --out_format .tif --output_dir ./outputs --max_retry 5 --retry_delay 10`

| **Parameter**           | **Description**                                                                                                                                                                                                                                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--product TEXT`        | The product code to retrieve.                                                                                                                                                                                                                                                                                     |
| `--dt TEXT`             | The date and time of the product to retrieve in ISO format (`YYYY-MM-DDTHH:MM:SS`). If not provided, the last available product will be retrieved.                                                                                                                                                                |
| `--bbox TEXT`           | The bounding box to clip the data, in the format `'minx,miny,maxx,maxy'`. If not provided, the entire product will be retrieved.                                                                                                                                                                                  |
| `--t_srs TEXT`          | The target spatial reference system to reproject the data to, expected in EPSG format (e.g., `'EPSG:4326'`). If not provided, the original CRS will be used.                                                                                                                                                      |
| `--out_format TEXT`     | The output format for the data file (e.g., `.tif`, `.geotiff`, `.nc`, `.netcdf`). If not provided, the original format will be used.                                                                                                                                                                              |
| `--return_data`         | If set, the function will return the data as a byte string instead of a file reference.                                                                                                                                                                                                                           |
| `--output_dir TEXT`     | The directory where the output file will be saved. If not provided, the file will be saved in the current working directory.                                                                                                                                                                                      |
| `--s3_bucket TEXT`      | The S3 bucket to copy the data to. If not provided, the data will not be copied to S3.                                                                                                                                                                                                                            |
| `--s3_catalog`          | If set, the function will register the availability of the product in the S3 catalog file.                                                                                                                                                                                                                        |
| `--max_retry INTEGER`   | The maximum number of retries to attempt in case of failure. Default is `3`.                                                                                                                                                                                                                                      |
| `--retry_delay INTEGER` | The delay in seconds between retries. Default is `60` seconds.                                                                                                                                                                                                                                                    |
| `--status`              | If set, the function will list the status of available products and exit without performing any retrieval. Useful for checking available products before making a request. Can be combined with `--product` to list details of a specific product or with `--verbose` to print details of all available products. |
| `--backend TEXT`        | The backend to use for sending progress status updates to the backend server.                                                                                                                                                                                                                                     |
| `--jid TEXT`            | The job ID to use for sending progress status updates to the backend server. If not provided, it will be generated automatically.                                                                                                                                                                                 |
| `--version`             | Show the version of the package.                                                                                                                                                                                                                                                                                  |
| `--debug`               | Enable debug mode.                                                                                                                                                                                                                                                                                                |
| `--verbose`             | Print more detailed information about the process.                                                                                                                                                                                                                                                                |
| `--help`                | Show this help message and exit.                                                                                                                                                                                                                                                                                  |

#### dpc-crontab
- `dpc-crontab --help`
- `dpc-crontab --output_file dpc-crontab.txt --dt_strategy now --output_dir ./output --debug`
- `dpc-crontab --output_file dpc-crontab.txt --dt_strategy last --output_dir ./output --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog --last`

| **Parameter**           | **Description**                                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `--products TEXT`       | List of product codes to include in the crontab. If not provided, all available products will be used.                |
| `--output_file TEXT`    | Output file for the generated crontab.                                                                                |
| `--dt_strategy TEXT` | Strategy for date and time: `NOW` for current time, `LAST` for last available data.                                |
| `--bbox TEXT`           | Bounding box in the format `"minx,miny,maxx,maxy"`. If not provided, no bounding box will be applied.                 |
| `--t_srs TEXT`          | Target spatial reference system in EPSG format (e.g., `"EPSG:4326"`). If not provided, the original CRS will be used. |
| `--output_dir TEXT`     | Directory where the output files will be saved. If not provided, the current working directory will be used.          |
| `--s3_bucket TEXT`      | S3 bucket to copy the data to. If not provided, the data will not be copied to S3.                                    |
| `--s3_catalog`          | If set, the function will register the availability of the product in the S3 catalog file.                            |
| `--max_retry INTEGER`   | Maximum number of retries to attempt in case of failure. Default is `3`.                                              |
| `--retry_delay INTEGER` | Delay in seconds between retries. Default is `60` seconds.                                                            |
| `--debug`               | Enable debug mode for detailed logging.                                                                               |
| `--help`                | Show this help message and exit.                                                                                      |


#### dpc-shp-concat
- `dpc-shp-concat --help`
- `dpc-shp-concat --src ./output --prefix 01-07-2025 --debug --out ./output/01-07-2025.shp --remove_src `

| **Parameter**     | **Description**                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `--src TEXT`      | Source directory containing shapefiles to concatenate. **Required.**                                                      |
| `--prefix TEXT`   | Prefix to filter shapefiles by name.                                                                                      |
| `--suffix TEXT`   | Suffix to filter shapefiles by name.                                                                                      |
| `--contains TEXT` | Substring to filter shapefiles by name.                                                                                   |
| `--out TEXT`      | Output path for the concatenated shapefile. If not provided, defaults to a new shapefile created in the source directory. |
| `--remove_src`    | If set, removes the source shapefiles after concatenation.                                                                |
| `--debug`         | Enable debug mode for detailed logging.                                                                                   |
| `--help`          | Show this help message and exit.                                                                                          |
