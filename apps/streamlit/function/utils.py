""" Utils functions """

import time
from typing import List
import numpy as np
import json

import torch
import torchvision


def parse_coco(json_file):
    """Parse COCO annotations from xywh to xyxy annotations format"""

    labels = json.load(open(json_file))

    ANNOTATIONS = []
    SCORES = []
    for dicts in labels["annotations"]:
        bbox = [bb for bb in dicts["bbox"]]
        # convert to xyxy
        dicts["bbox"] = xywh2xyxy(bbox)

        ANNOTATIONS.append(dicts)
        SCORES.append(1.00)

    return ANNOTATIONS, SCORES

def apply_nms(
    json_file: str,
    annotations: List,
    scores: List,
    iou_threshold: float,
    dump_json: bool = True,
):
    """Apply NMS to new COCO annotations, return new coco labels"""

    labels = json.load(open(json_file))
    # conver to tensor
    boxes = torch.tensor([boxes["bbox"] for boxes in annotations])
    scores = torch.tensor(scores)
    # apply nms
    nms = torchvision.ops.nms(boxes, scores, iou_threshold).tolist()
    # change annotations
    labels["annotations"] = [labels["annotations"][index] for index in nms]

    if dump_json:
        json_object = json.dumps(labels, indent=4)
        with open(json_file, "w") as f:
            f.write(json_object)

    return labels


def xywh2xyxy(bbox):
    x1, y1, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
    x2, y2 = round(w + x1, 2), round(h + y1, 2)

    return [x1, y1, x2, y2]


if __name__ == "__main__":

    labels_path = (
        "/home/intern-didir/Repository/labelling/apps/streamlit/41/labels.json"
    )

    annots, scores = parse_coco(json_file=labels_path)

    labels = apply_nms(
        json_file=labels_path,
        annotations=annots,
        scores=scores,
        iou_threshold=0.5,
        dump_json=True,
    )
