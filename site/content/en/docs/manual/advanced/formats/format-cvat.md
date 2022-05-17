---
linkTitle: "CVAT"
weight: 1
---

# CVAT

This is the native CVAT annotation format. It supports all CVAT annotations
features, so it can be used to make data backups.

- supported annotations CVAT for Images: Rectangles, Polygons, Polylines,
  Points, Cuboids, Tags, Tracks

- supported annotations CVAT for Videos: Rectangles, Polygons, Polylines,
  Points, Cuboids, Tracks

- attributes are supported

- [Format specification](/docs/manual/advanced/xml_format/)

## CVAT for images export

Downloaded file: a ZIP file of the following structure:

```bash
taskname.zip/
├── images/
|   ├── img1.png
|   └── img2.jpg
└── annotations.xml
```

- tracks are split by frames

## CVAT for videos export

Downloaded file: a ZIP file of the following structure:

```bash
taskname.zip/
├── images/
|   ├── frame_000000.png
|   └── frame_000001.png
└── annotations.xml
```

- shapes are exported as single-frame tracks

## CVAT loader

Uploaded file: an XML file or a ZIP file of the structures above
