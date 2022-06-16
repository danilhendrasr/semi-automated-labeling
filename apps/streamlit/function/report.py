""" Generate Dataset Report """

from mdutils.mdutils import MdUtils
from fiftyone51 import convert_to_yolo

class Report:
    def __init__(self, filename: str, title: str):
        self.filename = filename
        self.title = title

    def generate(self):
        """Generate report"""
        markdown = MdUtils(file_name=self.filename, title=self.title)

        markdown.create_md_file()

if __name__ == '__main__':

    title = 'Sample Dataset Report'
    filename = 'README'

    report = Report(filename=filename, title=title)
    report.generate()
    
