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

def load(dataset_dir, label_tags=None):
    if label_tags is None: label_tags = []
    if label_tags == 'all':
        label_tags = set()
        with open(os.path.join(dataset_dir, 'labels.json'), 'r') as f:
            data = json.load(f)
            for annotation in data['annotations']:
                for label_tag in annotation['attributes']:
                    label_tags.add(label_tag)
        label_tags = list(label_tags)
    
    dataset = fo.Dataset.from_dir(
        dataset_dir=dataset_dir,
        dataset_type=fo.types.COCODetectionDataset
    )
    
    for sample in dataset:
        for detection in sample.ground_truth.detections:
            for label_tag in label_tags:
                if label_tag in detection:
                    detection.tags.append(label_tag)
        sample.save()
        
    return dataset

def save(dataset, labels_path, label_tags=None):
    if label_tags is None: label_tags = []
    if label_tags == 'all':
        label_tags = set()
        for sample in dataset:
            for detection in sample.ground_truth.detections:
                for label_tag in detection.tags:
                    label_tags.add(label_tag)
        label_tags = list(label_tags)
    
    for sample in dataset:
        for detection in sample.ground_truth.detections:
            for label_tag in label_tags:
                if label_tag in detection.tags:
                    detection[label_tag] = True
        sample.save()
    
    dataset.export(
        dataset_type=fo.types.COCODetectionDataset,
        labels_path=labels_path,
        label_field='ground_truth',
    )
    
    with open(labels_path, 'r') as f:
        data = json.load(f)
    
    for i, annotation in enumerate(data['annotations']):
        annotation['attributes'] = dict()
        for label_tag in label_tags:
            if label_tag in annotation: annotation['attributes'][label_tag] = annotation[label_tag]
        data['annotations'][i] = annotation
    
    with open(labels_path, 'w') as f:
        json.dump(data, f)

def filter_tags(dataset, label_tags):
    idx = []
    for i, sample in enumerate(dataset):
        found = False
        for detection in sample.ground_truth.detections:
            if found: break
            for label_tag in label_tags:
                if found: break
                if label_tag in detection.tags:
                    idx.append(i)
                    found = True
    return idx