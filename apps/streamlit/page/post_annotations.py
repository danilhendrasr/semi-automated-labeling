""" Post Annotations Page """

import os
import streamlit as st
from section import cvat as sec_cvat

from function import fiftyone51
from function import cvat
from function import utils


def post_annotations(
    page_key: str = "post_annotations", dump_dir: str = os.getcwd(), port: int = 5151
):

    st.header("Post Annotations")
    username, password, iou_thres, task_id, btn = sec_cvat.export_dataset_fiftyone(
        section_key=page_key
    )
    dataset_dir = os.path.join(dump_dir, task_id)

    if btn:
        dataset = cvat.CVAT(
            username=username,
            password=password,
            host="http://192.168.103.67:8080",
            dump_dir=dump_dir,
        )

        dataset.tasks_dump(
            task_id=task_id,
            fileformat="COCO 1.0",
            filename=f"{task_id}.zip",
            extract=True,
        )
        st.success(f'[INFO] Download Dataset Task {task_id}')

        # apply nms
        # TODO: maybe create another page/section
        json_file_path = os.path.join(
            dataset_dir, "annotations", "instances_default.json"
        )
        annots, scores = utils.parse_coco(json_file=json_file_path)
        utils.apply_nms(
            json_file=json_file_path,
            annotations=annots,
            scores=scores,
            iou_threshold=float(iou_thres),
            dump_json=True,
        )
        st.success('[INFO] Apply NMS')

        fiftyone51.convert_to_coco(dataset_dir=dataset_dir)
        st.success('[INFO] Convert to FiftyOne COCO Format')

        fiftyone51.preview_fiftyone(
            dataset_name=task_id,
            dataset_dir=dataset_dir,
            delete_existing=True,
            port=port,
        )
        st.success('[INFO] Load to FiftyOne')
