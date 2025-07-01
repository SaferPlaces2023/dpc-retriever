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
- `dpc-retriever --product SRI --dt last --bbox 12,45.15,12.7,45.6 --t_srs 'EPSG:4326' --out_format '.tif' --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog`
- `dpc-retriever --product SRI --dt 2025-06-30T10:55:00 --bbox 12,45.15,12.7,45.6 --t_srs 'EPSG:4326' --out_format '.tif' --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog --max_retry 5 --retry_delay 10`
- `dpc-retriever --product SRI --bbox 12,45.15,12.7,45.6 --t_srs 'EPSG:4326' --out_format '.tif' --output_dir ./outputs --max_retry 5 --retry_delay 10`

#### dpc-crontab
- `dpc-crontab --output_file dpc-crontab.txt --dt_strategy now --output_dir ./output --debug`
- `dpc-crontab --output_file dpc-crontab.txt --dt_strategy last --output_dir ./output --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog --last`

#### dpc-shp-concat
- `dpc-shp-concat --src ./output --prefix 01-07-2025 --debug --out ./output/01-07-2025.shp --remove_src `