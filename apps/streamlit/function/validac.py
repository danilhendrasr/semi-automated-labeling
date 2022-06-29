"""Dataset validation"""

import fiftyone as fo
import os


class Validac:
    """Validac dataset gt with dataset prediction"""

    def __init__(self, gt_id: str, pred_id: str, iou_threshold: float, dump_dir: str = os.getcwd()):

        list_datasets = fo.list_datasets()
        try:
            [fo.delete_dataset(name) for name in list_datasets]
        except:
            print("[INFO] No Existing Dataset")

        # load dataset with fiftyone
        self.dataset_gt = fo.Dataset.from_dir(
            dataset_dir=os.path.join(dump_dir, gt_id),
            dataset_type=fo.types.COCODetectionDataset,
            name=str(gt_id),
            label_field="ground_truth",
        )
        self.dataset_pred = fo.Dataset.from_dir(
            dataset_dir=os.path.join(dump_dir, pred_id),
            dataset_type=fo.types.COCODetectionDataset,
            name=str(pred_id),
            label_field="prediction",
        )

        # add confidence to dataset_pred
        for sample in self.dataset_pred:
            for attribute in sample.prediction.detections:
                attribute["confidence"] = 1.0
            sample.save()

        # merge dataset_gt and dataset_pred
        for sample_gt, sample_pred in zip(self.dataset_gt, self.dataset_pred):
            sample_gt["predictions"] = fo.Detections(
                detections=sample_pred.prediction.detections
            )

            sample_gt.save()

        # results
        self.results = None
        self.iou_threshold = iou_threshold


    def compute_mAP(self):
        """Validac dataset gt with dataset prediction"""
        self.results = self.dataset_gt.evaluate_detections(
            pred_field="predictions",
            gt_field="ground_truth",
            iou_threshold=self.iou_threshold,
            eval_key="eval",
            compute_mAP=True,
        )

        return self.results.mAP()

    def preview_evaluation(self):
        """validate dataset with COCO"""
        dataset_eval = self.dataset_gt.to_evaluation_patches("eval")

        fo.launch_app(dataset=dataset_eval, address="0.0.0.0", port=6161)

        return dataset_eval