""" Generate Dataset Report """

from glob import glob
import shutil
from mdutils.mdutils import MdUtils
import os
import math

import fiftyone as fo
import fiftyone.brain as fob
from fiftyone import ViewField as F
from function.fiftyone51 import fiftyone_format

class GenerateReport:
    """ 
    Automatic Generate Report based on FiftyOne Dataset Format 
    IMPORTANT: must on FiftyOne Dataset Format
    """
    def __init__(
        self,
        repo_dir: str,
        format: str,
        version: str,
        desc: str,
        filename: str = "README"
        
    ):
        self.repo_dir = repo_dir
        self.format = format
        self.version = version
        self.dataset_dir = os.path.join(self.repo_dir, 'dataset')
        self.desc = desc

        # create directory
        assets_dir = os.path.join(self.repo_dir, 'assets')
        self.plot_dir = os.path.join(assets_dir, 'plot')
        self.example_dir = os.path.join(assets_dir, 'images')
        if not os.path.isdir(assets_dir):
            os.makedirs(self.plot_dir)
            os.makedirs(self.example_dir)
        else:
            shutil.rmtree(assets_dir)
            os.makedirs(self.plot_dir)
            os.makedirs(self.example_dir)

        # delete fiftyone
        list_datasets = fo.list_datasets()
        try:
            [fo.delete_dataset(name) for name in list_datasets]
        except:
            print("[INFO] No Existing Dataset")

        # initiate dataset
        dataset_type = fiftyone_format(format)
        self.dataset = fo.Dataset.from_dir(
            dataset_dir=self.dataset_dir,
            dataset_type=dataset_type,
        )
        self.dataset.compute_metadata()

        # initiate report markdown
        self.md = MdUtils(file_name=filename, title="Dataset Report") 

    def plot_imagebytes(self, save_img: bool = True):
        """plot image size in KB"""
        plot = fo.NumericalHistogram(
            F("metadata.size_bytes") / 1024,
            bins=50,
            xlabel="image size (KB)",
            init_view=self.dataset,
        )
        if save_img:
            plot.save(f"{self.plot_dir}/hist_imagebytes.svg", scale=2.0)

    def plot_gtlabel(self, save_img: bool = True):
        """plot object gt label"""
        plot = fo.CategoricalHistogram(
            "ground_truth.detections.label",
            order="frequency",
            xlabel="ground truth label",
            init_view=self.dataset,
        )
        if save_img:
            plot.save(f"{self.plot_dir}/hist_gtlabel.svg", scale=2.0)

    def plot_uniqueness(self, save_img: bool = True):
        """plot image uniqueness"""
        fob.compute_uniqueness(self.dataset)
        results = fob.compute_visualization(self.dataset)
        plot = results.visualize(
            labels="uniqueness",
            axis_equal=True,
        )
        if save_img:
            plot.save(f"{self.plot_dir}/uniqueness.svg", scale=2.0)

    def plot_embeddings_object(self, save_img: bool = True):
        """plot object (bounding-box) embeddings"""
        results = fob.compute_visualization(self.dataset, patches_field="ground_truth")
        bbox_area = F("bounding_box")[2] * F("bounding_box")[3]
        plot = results.visualize(
            labels=F("ground_truth.detections.label"),
            sizes=F("ground_truth.detections[]").apply(bbox_area),
        )
        if save_img:
            plot.save(f"{self.plot_dir}/embedding.svg", scale=2.0)

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

    def description(self):
        """Generap purpose section"""
        self.md.new_header(level=2, title="Description")
        stats = self.stats()
        table = ["Information", "Description"]
        description = [self.version, self.format, stats[0], stats[1], stats[2], stats[3], stats[4]]
        index = [
            "Dataset Version",
            "Annotation File Format",
            "Data Type",
            "Number of Class",
            "Classes",
            "Number of Samples",
            "Total Size"
        ]
        for i in range(len(index)):
            table.extend([index[i], description[i]])
        self.md.new_table(columns=2, rows=len(index) + 1, text=table, text_align="left")

    def whats_new(self):
        self.md.new_header(level=2, title="What's New")
        table = ["Version", "News", self.version, self.desc]
        self.md.new_table(columns=2, rows=2, text=table, text_align="left")

    def dataset_structure(self):
        """Dataset structure"""
        os.chdir(self.dataset_dir)
        tree = os.popen(f"tree --filelimit=5").read()

        self.md.new_header(level=2, title="Dataset Structure")
        self.md.new_paragraph(f"```\n{tree}\n```")

    def dataset_distribution(self):
        """Plot dataset distribution"""
        assets = [f"./assets/plot/{asset}" for asset in os.listdir(self.plot_dir)]
        self.md.new_header(level=2, title="Dataset Distribution")
        table = ["", ""]  # two columns
        for i in range(0, len(assets), 2):
            if i == len(assets) - 1:
                table.extend([self.md.new_inline_image(assets[i].split("/")[-1], assets[i]), ""])
            else:
                table.extend([self.md.new_inline_image(assets[i].split("/")[-1], assets[i]),
                            self.md.new_inline_image(assets[i + 1].split("/")[-1], assets[i + 1])])
        self.md.new_table(columns=2, rows=math.ceil(len(assets) / 2) + 1, text=table, text_align="center")

    def dataset_example(self):
        """Plot dataset example"""
        # list images and labels from dataset
        assets_path = os.path.join(self.example_dir)
        images = glob(os.path.join(self.repo_dir, 'dataset', 'data', '*.jpg'))[:4]
        [shutil.copy2(images[i], assets_path) for i in range(len(images))]
        # list new images and labels from dataset
        assets = sorted([f"./assets/images/{asset}" for asset in os.listdir(assets_path)])
        self.md.new_header(level=2, title="Dataset Example")
        table = ["", ""]  # two columns
        for i in range(0, len(assets), 2):
            table.extend([self.md.new_inline_image(assets[i].split("/")[-1], assets[i]),
                        self.md.new_inline_image(assets[i + 1].split("/")[-1], assets[i + 1])])
        self.md.new_table(columns=2, rows=math.ceil(len(assets) / 2) + 1, text=table, text_align="center")

    def generate(self):
        """Generate Plot and Report"""
        self.plot_imagebytes()
        self.plot_gtlabel()
        # self.plot_uniqueness()
        self.plot_embeddings_object()

        self.md.new_header(level=1, title="")
        self.md.new_line()
        self.description()
        self.whats_new()
        self.dataset_structure()
        self.dataset_distribution()
        self.dataset_example()

        os.chdir(self.repo_dir)
        self.md.create_md_file()

if __name__ == "__main__":

    report = GenerateReport(
        repo_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump/ruhyadi/dataset-registry-002",
        format="YOLO 1.1",
        version="v1.0",
        desc="Add new 20 data",
        filename="README"
    )
    report.generate()
