""" FiftyOne Functions """

import fiftyone as fo
import os

def convert_to_coco(dataset_dir):
    """ Convert from COCO CVAT format to Fiftyone format """
    # rename directory images to data
    src = os.path.join(dataset_dir, 'images')
    dst = os.path.join(dataset_dir, 'data')
    os.rename(src, dst)

    # rename instance_default.json to labels.json
    src_1 = os.path.join(dataset_dir, 'annotations', 'instances_default.json')
    dst_1 = os.path.join(dataset_dir, 'labels.json')
    os.rename(src_1, dst_1)

    print('[INFO] Success convert to Fiftyone COCO Format')

def preview_fiftyone(dataset_name: str, dataset_dir: str, 
                    delete_existing: bool = True, port: int = 5151):
    """ Preview dataset to FiftyOne Apps """
    # delete existing dataset
    if delete_existing:
        list_datasets = fo.list_datasets()
        try:
            [fo.delete_dataset(name) for name in list_datasets]
        except:
            print('[INFO] No Existing Dataset')
    
    dataset = fo.Dataset.from_dir(
        dataset_dir=dataset_dir,
        dataset_type=fo.types.COCODetectionDataset,
        name=dataset_name
    )

    fo.launch_app(dataset, address='0.0.0.0', port=port)