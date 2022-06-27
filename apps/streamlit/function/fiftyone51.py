""" FiftyOne Functions """

import shutil
from typing import List
import fiftyone as fo
from fiftyone import ViewField as F
import fiftyone.brain as fob

import os
import json
from glob import glob
import time


def convert_to_coco(dataset_dir):
    """Convert from COCO CVAT format to Fiftyone format"""
    # rename directory images to data
    src = os.path.join(dataset_dir, "images")
    dst = os.path.join(dataset_dir, "data")
    os.rename(src, dst)

    # rename instance_default.json to labels.json
    src_1 = os.path.join(dataset_dir, "annotations", "instances_default.json")
    dst_1 = os.path.join(dataset_dir, "labels.json")
    os.rename(src_1, dst_1)

    print("[INFO] Success convert to Fiftyone COCO Format")


def convert_to_yolo(dataset_dir):
    """Convert from YOLO CVAT format to Fiftyone format"""
    # rename directory images to data
    src = os.path.join(dataset_dir, "obj_train_data")
    dst = os.path.join(dataset_dir, "data")
    os.rename(src, dst)

    dst_files = sorted(glob(os.path.join(dataset_dir, "data", "*.jpg")))
    with open(os.path.join(dataset_dir, "images.txt"), "w") as f:
        for file in dst_files:
            f.write(f"{'/'.join(file.split('/')[-2:])}\n")

    os.remove(dataset_dir, "train.txt")

    print("[INFO] Success convert to Fiftyone YOLO Format")


def preview_fiftyone(
    dataset_name: str,
    dataset_dir: str,
    delete_existing: bool = True,
    is_patches: bool = True,
    port: int = 5151,
):
    """Preview dataset to FiftyOne Apps"""
    # delete existing dataset
    if delete_existing:
        list_datasets = fo.list_datasets()
        try:
            [fo.delete_dataset(name) for name in list_datasets]
        except:
            print("[INFO] No Existing Dataset")

    dataset = fo.Dataset.from_dir(
        dataset_dir=dataset_dir,
        dataset_type=fo.types.COCODetectionDataset,
        name=dataset_name,
    )

    session = fo.launch_app(dataset, address="0.0.0.0", port=port)

    if is_patches:
        # view mode patches ground truth/predictions
        gt_patches = dataset.to_patches("ground_truth")
        session.view = gt_patches
        return dataset, gt_patches
    else:
        session.view = None
        return dataset


def get_tags(patches):
    """get patches tags"""
    TAGS = []
    for pred in patches:
        try:
            TAGS.append(pred.ground_truth.tags[0])
        except:
            TAGS.append("null")

    return TAGS


def convert_labels(
    dataset_dir: str, from_tag: str, to_label: str, list_tags: List, category_id: List
):
    """Convert COCO labels based on fiftyone tags"""
    # load coco labels
    labels_json = json.load(open(os.path.join(dataset_dir, "labels.json")))

    label_index = category_id.index(to_label)

    for i, annotations in enumerate(labels_json["annotations"]):
        if list_tags[i] == from_tag:
            annotations["category_id"] = label_index

    # save coco json
    with open(os.path.join(dataset_dir, "labels.json"), "w") as f:
        f.write(json.dumps(labels_json))


def save_tags_patches(patches, dataset_dir: str):
    """Save fiftyone tags to COCO json dataset format"""

    # iterates tags in dataset
    tags = []
    for pred in patches:
        try:
            tags.append({(pred.ground_truth.tags)[0]: True})
        except:
            tags.append(None)

    # load coco json
    labels_json = json.load(open(os.path.join(dataset_dir, "labels.json")))

    index = []
    for i, annot in enumerate(labels_json["annotations"]):
        # change tags according to fiftyone tags
        if tags[i] is not None:
            annot["attributes"] = tags[i]
            index.append(i)
        else:
            pass

    # save coco json
    with open(os.path.join(dataset_dir, "labels.json"), "w") as f:
        f.write(json.dumps(labels_json))

    return index


def load(dataset_dir, label_tags=None):
    if label_tags is None:
        label_tags = []
    if label_tags == "all":
        label_tags = set()
        with open(os.path.join(dataset_dir, "labels.json"), "r") as f:
            data = json.load(f)
            for annotation in data["annotations"]:
                for label_tag in annotation["attributes"]:
                    label_tags.add(label_tag)
        label_tags = list(label_tags)

    dataset = fo.Dataset.from_dir(
        dataset_dir=dataset_dir, dataset_type=fo.types.COCODetectionDataset
    )

    for sample in dataset:
        for detection in sample.ground_truth.detections:
            for label_tag in label_tags:
                if label_tag in detection:
                    detection.tags.append(label_tag)
        sample.save()

    return dataset


def save(dataset, labels_path, label_tags=None):
    if label_tags is None:
        label_tags = []
    if label_tags == "all":
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
        label_field="ground_truth",
    )

    with open(labels_path, "r") as f:
        data = json.load(f)

    for i, annotation in enumerate(data["annotations"]):
        annotation["attributes"] = dict()
        for label_tag in label_tags:
            if label_tag in annotation:
                annotation["attributes"][label_tag] = annotation[label_tag]
        data["annotations"][i] = annotation

    with open(labels_path, "w") as f:
        json.dump(data, f)


def filter_tags(dataset, label_tags):
    idx = []
    for i, sample in enumerate(dataset):
        found = False
        for detection in sample.ground_truth.detections:
            if found:
                break
            for label_tag in label_tags:
                if found:
                    break
                if label_tag in detection.tags:
                    idx.append(i)
                    found = True
    return idx

def fiftyone_format(select: str):

    format = {
        "COCO 1.0": fo.types.COCODetectionDataset,
        "YOLO 1.1": fo.types.YOLOv4Dataset,
        "CVAT 1.1": fo.types.CVATImageDataset
    }

    return format[select]

def convert_format(dataset_dir: str, format: str):
    """Convert CVAT to FiftyOne Format"""
    dataset_type = fiftyone_format(format)
    # create dump directory
    dump_dataset = os.path.join(dataset_dir, "dump")
    os.makedirs(dump_dataset)

    src = os.path.join(dataset_dir, "images")
    dst = os.path.join(dump_dataset, "data")
    os.rename(src, dst)
    src = os.path.join(dataset_dir, "annotations", "instances_default.json")
    dst = os.path.join(dump_dataset, "labels.json")
    os.rename(src, dst)

    dataset = fo.Dataset.from_dir(dump_dataset, fo.types.COCODetectionDataset)
    # export dataset with fiftyone format
    dataset.export(dataset_dir, dataset_type)
    # delete old dataset
    shutil.rmtree(dump_dataset)
    shutil.rmtree(os.path.join(dataset_dir, "annotations"))

    print("[INFO] Success convert to FiftyOne CVAT Format")

def merging_dataset(format: str, repo_dir: str):
    """
    Merging dataset with FiftyOne
    new dataset path = repo_dir/new_dataset
    old dataset path = repo_dir/old_dataset
    """
    dataset_type = fiftyone_format(format)

    dataset_old = fo.Dataset.from_dir(
        dataset_dir=os.path.join(repo_dir, "old_dataset"), # fix
        dataset_type=dataset_type,
    )
    dataset_new = fo.Dataset.from_dir(
        dataset_dir=os.path.join(repo_dir, "new_dataset"), # fix
        dataset_type=dataset_type,
    )
    dataset_old.merge_samples(dataset_new)

    export_dir = os.path.join(repo_dir, "dataset")
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)
    else:
        shutil.rmtree(export_dir)
        os.makedirs(export_dir)
    # export dataset
    dataset_old.export(
        export_dir=export_dir,
        dataset_type=dataset_type
    )
    # remove old and new dataset
    shutil.rmtree(os.path.join(repo_dir, "old_dataset"))
    shutil.rmtree(os.path.join(repo_dir, "new_dataset"))

if __name__ == "__main__":
    pass

    # report.plot_imagebytes()
    # report.plot_gtlabel()
    # report.plot_uniqueness()
    # report.plot_embeddings_object()
    # report.preview_fiftyone(is_patches=True, port=6161)

    # print(report.dataset.get_classes('ground_truth'))
    # print(report.dataset.summary())
    # print(report.dataset.stats(include_media=True))
    # sample = report.dataset.first()
    # print(sample.metadata['mime_type']
