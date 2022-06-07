""" Post Annotations Page """

import os
import streamlit as st
from section import cvat as sec_cvat

from function import fiftyone51
from function import cvat

def post_annotations(page_key: str = 'post_annotations', dump_dir: str = os.getcwd(), port: int = 5151):

    st.header('Post Annotations')
    username, password, task_id, btn = sec_cvat.export_dataset_fiftyone(section_key=page_key)
    dataset_dir = os.path.join(dump_dir, task_id)

    if btn:
        dataset = cvat.CVAT(username=username, password=password, 
                host='http://192.168.103.67:8080', dump_dir=dump_dir)

        dataset.tasks_dump(task_id=task_id, fileformat='COCO 1.0', 
                filename=f'{task_id}.zip', extract=True)

        fiftyone51.convert_to_coco(dataset_dir=dataset_dir)

        fiftyone51.preview_fiftyone(dataset_name=task_id, dataset_dir=dataset_dir,
                delete_existing=True, port=port)