""" Generate Dataset Report """

from typing import TypedDict
from mdutils.mdutils import MdUtils
import os
import math
from fiftyone51 import convert_to_yolo


class GeneralPurposeOption(TypedDict):
    """Option for generate general purpose"""
    dataset_version: str
    data_type: str
    annot_format: str
    class_num: int
    num_img: int


class Report:
    def __init__(
        self,
        filename: str,
        repo_dir: str,
        dump_dir: str,
        title: str,
        news: str,
        opt_description: GeneralPurposeOption,
    ):
        self.filename = filename
        self.title = title
        self.news = news
        self.repo_dir = repo_dir
        self.assets_dir = "./assets"
        self.dump_dir = dump_dir
        self.opt_description = opt_description

        self.md = MdUtils(file_name=self.filename, title=self.title)

    def description(self):
        """Generap purpose section"""
        self.md.new_header(level=2, title="Description")
        table = ["Information", "Description"]
        index = [
            "Dataset Version",
            "Data Type",
            "Annotation File Format",
            "Class Number",
            "Number of Images",
        ]
        for i in range(len(index)):
            table.extend([index[i], self.opt_description[i]])
        self.md.new_table(columns=2, rows=len(index) + 1, text=table, text_align="left")

    def whats_new(self):
        self.md.new_header(level=2, title="What's New")
        table = ["Version", "News", self.opt_description[0], self.news]
        self.md.new_table(columns=2, rows=2, text=table, text_align="left")

    def dataset_structure(self):
        """Dataset structure"""
        dataset_dir = os.path.join(self.repo_dir, "dataset")
        os.chdir(dataset_dir)
        tree = os.popen(f"tree --filelimit=5").read()

        self.md.new_header(level=2, title="Dataset Structure")
        self.md.new_paragraph(f"```\n{tree}\n```")

    def dataset_distribution(self):
        assets = [f"./assets/{asset}" for asset in os.listdir(os.path.join(self.repo_dir, "assets"))]
        self.md.new_header(level=2, title="Dataset Distribution")
        table = ["", ""]  # two columns
        for i in range(0, len(assets), 2):
            if i == len(assets) - 1:
                table.extend([self.md.new_inline_image(assets[i].split("/")[-1], assets[i]), ""])
            else:
                table.extend([self.md.new_inline_image(assets[i].split("/")[-1], assets[i]),
                            self.md.new_inline_image(assets[i + 1].split("/")[-1], assets[i + 1])])
        self.md.new_table(columns=2, rows=math.ceil(len(assets) / 2) + 1, text=table, text_align="center")

    def generate(self):
        """Generate report"""
        self.md.new_header(level=1, title="Dataset Report")
        self.md.new_line()
        # description
        self.description()
        # whats new
        self.whats_new()
        # dataset structure
        self.dataset_structure()
        # dataset distribution
        self.dataset_distribution()

        os.chdir(self.dump_dir)
        self.md.create_md_file()

if __name__ == "__main__":

    title = "Sample Dataset Report"
    filename = "README"

    report = Report(
        filename=filename,
        title=title,
        news="Penambahan",
        repo_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump/ruhyadi/sample-dataset-registry",
        dump_dir="/home/intern-didir/Repository/labelling/apps/streamlit/dump/ruhyadi/sample-dataset-registry",
        opt_description=["v1.0", ".jpg", "YOLO", "42", "1000"],
    )
    report.generate()
