# Dataset-Utils

This repository is created to process data labels in the field of detection,

`voc2coco` contains function which can convert pascal voc `.xml` to coco `.json` format.

`datasetutils` can transform images with annotations to low resolution images with annotations.



# voc2coco

You can get the image annotations by [labelImg](https://github.com/tzutalin/labelImg). 

It's usually Pascal VOC format.  The file directory is as follows:

```shell
MarkerDataset
├── annotations
│   ├── 000000.xml
│   ├── 000001.xml
│   ├── ...
│   └── ...
├── images
│   ├── 000000.jpg
│   ├── 000001.jpg
│   ├── ...
│   └── ...
├── coco_output.json # convert function output this file
├── except.txt # contains some xml which don't have boox
└── xmllist.txt # contains all xml file names in annotations dir

```

To convert voc to coco, we can use:

```shell
python voc2coco.py --xml_path /path/to/annotaions --xml_list_path /path/to/xmllist.txt --output_path /path/to/coco_output.json
```

It will create `xmllist.txt` and `except.txt`  which contain the name of xml files, and `coco_output.json` is coco format annotations.

**All these are used for my detection dataset**

# datasetutils

This file can transform high resolution images with annotations to low resolution images.

For example, My dataset have 25,000 images with annotations. The resolution is 1280×720. Use this python file to create a low resolution dataset. It contains 25,000 images with annotations, but resolution is changed to 640×360.  It also changed the `xml`  annotation file to match low resolution images.