if __name__ == "__main__":

    from dpc_retriever import DPCRetrieverProcessor

    processor_def = {
        "name": "dpc-retriever",
        "type": "process",
        "processor": {
            "name": "path.to.DPCRetrieverProcessor"
        }
    }

    processor = DPCRetrieverProcessor(processor_def)

    res = processor.execute(
        {
            "product": "SRI",
            "long_range": [11, 11.1],
            "lat_range": [44, 44.1],
            "time_range": ["2026-05-28T00:00:00", "2026-05-28T00:30:00"],

            "bucket_destination": f"s3://saferplaces.co/packages/dpc-retriever/tests/test-processor-freq",
            "t_srs": "EPSG:3857",
            "frequency": 60*15,

            "debug": True,
            'user': "safercast",
            'token': "token",
        }
    )

    print('\n\n\n', res, '\n\n\n')