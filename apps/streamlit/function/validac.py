"""Dataset validation"""

import fiftyone as fo
import fiftyone.brain as fob
from fiftyone import ViewField as F
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
        self.dump_dir = dump_dir

    def compute_results(self):
        """compute results"""
        self.results = self.dataset_gt.evaluate_detections(
            pred_field="predictions",
            gt_field="ground_truth",
            iou_threshold=self.iou_threshold,
            eval_key="eval",
            compute_mAP=True,
        )
        return self.results

    def compute_mAP(self):
        """Validac dataset gt with dataset prediction"""
        return self.results.mAP()

    def preview_evaluation(self):
        """validate dataset with COCO"""
        dataset_eval = self.dataset_gt.to_evaluation_patches("eval")
        fo.launch_app(dataset=dataset_eval, address="0.0.0.0", port=6161)
        return dataset_eval

    def confusion_matrix(self):
        """plot confusion matrix"""
        counts = self.dataset_gt.count_values("predictions.detections.label")
        classes = sorted(counts, key=counts.get, reverse=True)[:10]
        plot = self.results.plot_confusion_matrix(classes=classes, backend="matplotlib")
        return plot

    def embedding(self):
        # TODO: embeddings on gt and pred
        """plot object (bounding-box) embeddings"""
        results = fob.compute_visualization(self.dataset_gt, patches_field="predictions")
        bbox_area = F("bounding_box")[2] * F("bounding_box")[3]
        plot = results.visualize(
            labels=F("predictions.detections.label"),
            sizes=F("predictions.detections[]").apply(bbox_area),
        )
        plot.save(os.path.join(self.dump_dir, "embedding.png"))

    def gt_distribution(self):
        """plot distribution of ground-truth labels"""
        plot = fo.CategoricalHistogram(
            "ground_truth.detections.label",
            order="frequency",
            xlabel="ground truth label",
            init_view=self.dataset_gt,
        )
        plot.save(os.path.join(self.dump_dir, "gt_distribution.png"))

    def pred_distribution(self):
        """plot distribution of prediction labels"""
        plot = fo.CategoricalHistogram(
            "predictions.detections.label",
            order="frequency",
            xlabel="prediction label",
            init_view=self.dataset_gt,
        )
        plot.save(os.path.join(self.dump_dir, "pred_distribution.png"))

    def stats(self):
        """statistics about dataset"""
        stats = self.dataset_gt.stats(include_media=True)
        images = stats["samples_count"]
        annotations = sum([v for k, v in self.dataset_gt.count_values("predictions.detections.label").items()])
        size = stats["total_size"]

        return [images, annotations, size]



