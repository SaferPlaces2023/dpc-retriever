import unittest
from dpc_retriever import main_python

from dpc_retriever.dpc import products


class Test(unittest.TestCase):

    def test_product(self, product, dt=None, bbox=None, t_srs=None, out_format=None, return_data=False, s3_bucket=None, s3_catalog=False):
        """
        Test download and process a product.
        """
        
        result = main_python(
            product = product,
            dt = dt,
            bbox = bbox,
            t_srs = t_srs,
            out_format = out_format,
            return_data = return_data,
            s3_bucket = s3_bucket,
            s3_catalog = s3_catalog,
            
            debug = False,
        )
        
        print(result)
        
        # Check if the result is a valid file path or data structure
        self.assertTrue(
            result.get('status', 'KO') == 'OK' and result.get('body', dict()).get('data', '').startswith('s3://'),
            "The result should contain a valid S3 path or data structure."
        )
        


if __name__ == '__main__':
    
    test = Test()
    
    for product in products._ALL_PRODUCTS:
        
        # DOC:  --bbox 12,45.15,12.7,45.6 --t_srs 'EPSG:4326' --out_format '.tif' --return_data --s3_bucket s3://saferplaces.co/test/dpc-retriever --s3_catalog
        
        try:
            test.test_product(
                product = product.code,
                dt = None,  # Use last available datetime
                bbox = '12,45.15,12.7,45.6',
                t_srs = 'EPSG:4326',
                out_format = None,
                return_data = False,
                s3_bucket = 's3://saferplaces.co/test/dpc-retriever',
                s3_catalog = True
            )
            print(f">>> Test passed for product {product.code}")
        except Exception as e:
            print(f"XXX Test failed for product {product.code}: {e}")
        
    print("All tests completed successfully.")