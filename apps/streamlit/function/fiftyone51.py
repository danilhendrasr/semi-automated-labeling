""" FiftyOne Functions """

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


def get_tags(patches, dataset_dir: str = None):
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
    with open(os.path.join(dataset_dir, "labels2.json"), "w") as f:
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


class GeneratePlot:
    """Generate Report with FiftyOne"""

    def __init__(self, repo_dir: str, annotations_type: str):

        assert annotations_type in ["YOLO 1.1"], "Annotations does not support"

        self.dataset_dir = os.path.join(repo_dir, "dataset")
        self.save_dir = os.path.join(repo_dir, "assets", "plot")
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        if annotations_type == "YOLO 1.1":
            try:
                convert_to_yolo(dataset_dir=self.dataset_dir)
            except:
                print("[INFO] Dataset already in FiftyOne YOLO Format")

        self.dataset = fo.Dataset.from_dir(
            dataset_dir=self.dataset_dir,
            dataset_type=fo.types.YOLOv4Dataset,
        )
        # compute metadata
        self.dataset.compute_metadata()

    def preview_fiftyone(
        self, delete_existing: bool = True, is_patches: bool = False, port: int = 5151
    ):
        """DEPRICATED SOON"""
        """Preview dataset to FiftyOne Apps"""
        if delete_existing:
            list_datasets = fo.list_datasets()
            try:
                [fo.delete_dataset(name) for name in list_datasets]
            except:
                pass

        self.dataset = fo.Dataset.from_dir(
            dataset_dir=self.dataset_dir,
            dataset_type=fo.types.YOLOv4Dataset,
        )
        self.dataset.compute_metadata()

        session = fo.launch_app(self.dataset, address="0.0.0.0", port=port)
        if is_patches:
            # view mode patches ground truth/predictions
            gt_patches = self.dataset.to_patches("ground_truth")
            session.view = gt_patches
        else:
            session.view = None

        time.sleep(1000)

    def plot_imagebytes(self, save_img: bool = True):
        """plot image size in KB"""
        plot = fo.NumericalHistogram(
            F("metadata.size_bytes") / 1024,
            bins=50,
            xlabel="image size (KB)",
            init_view=self.dataset,
        )
        if save_img:
            plot.save(f"{self.save_dir}/hist_imagebytes.svg", scale=2.0)

    def plot_gtlabel(self, save_img: bool = True):
        """plot object gt label"""
        plot = fo.CategoricalHistogram(
            "ground_truth.detections.label",
            order="frequency",
            xlabel="ground truth label",
            init_view=self.dataset,
        )
        if save_img:
            plot.save(f"{self.save_dir}/hist_gtlabel.svg", scale=2.0)

    def plot_uniqueness(self, save_img: bool = True):
        """plot image uniqueness"""
        fob.compute_uniqueness(self.dataset)
        results = fob.compute_visualization(self.dataset)
        plot = results.visualize(
            labels="uniqueness",
            axis_equal=True,
        )
        if save_img:
            plot.save(f"{self.save_dir}/uniqueness.svg", scale=2.0)

    def plot_embeddings_object(self, save_img: bool = True):
        """plot object (bounding-box) embeddings"""
        results = fob.compute_visualization(self.dataset, patches_field="ground_truth")
        bbox_area = F("bounding_box")[2] * F("bounding_box")[3]
        plot = results.visualize(
            labels=F("ground_truth.detections.label"),
            sizes=F("ground_truth.detections[]").apply(bbox_area),
        )
        if save_img:
            plot.save(f"{self.save_dir}/embedding.svg", scale=2.0)

    def generate(self):
        """Generate Plot"""
        self.plot_imagebytes()
        self.plot_gtlabel()
        self.plot_uniqueness()
        self.plot_embeddings_object()

    def stats(self):
        """Return dataset stats"""
        classes = self.dataset.get_classes("ground_truth")
        num_classes = len(classes)
        stats = self.dataset.stats(include_media=True)
        num_samples = stats["samples_count"]
        total_size = stats["total_size"]
        sample = self.dataset.first()
        dataset_type = sample.metadata["mime_type"]

        return [dataset_type, num_classes, str(classes), num_samples, total_size]


if __name__ == "__main__":

    # test generate report
    report = GeneratePlot(
        repo_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump/ruhyadi/sample-dataset-registry",
        annotations_type="YOLO 1.1",
    )
    # report.plot_imagebytes()
    # report.plot_gtlabel()
    # report.plot_uniqueness()
    # report.plot_embeddings_object()
    # report.preview_fiftyone(is_patches=True, port=6161)

    # print(report.dataset.get_classes('ground_truth'))
    # print(report.dataset.summary())
    # print(report.dataset.stats(include_media=True))
    # sample = report.dataset.first()
    # print(sample.metadata['mime_type'])
