#!/usr/bin/python

# pip install lxml

import sys
import os
import json
import xml.etree.ElementTree as ET
import pathlib
import argparse

# If necessary, pre-define category and its id
START_BOUNDING_BOX_ID = 1
PRE_DEFINE_CATEGORIES = {"marker": 1}


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars


def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(filename)[0]
        return int(filename)
    except:
        raise NotImplementedError('Filename %s is supposed to be an integer.'%(filename))


def convert(xml_list, xml_dir, json_file):
    list_fp = open(xml_list, 'r')
    json_dict = {"images":[], "type": "instances", "annotations": [],
                 "categories": []}
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:
        line = line.strip()
        print("Processing %s"%(line))
        xml_f = os.path.join(xml_dir, line)
        tree = ET.parse(xml_f)
        root = tree.getroot()
        path = get(root, 'path')
        if len(path) == 1:
            filename = os.path.basename(path[0].text)
        elif len(path) == 0:
            filename = get_and_check(root, 'filename', 1).text
        else:
            raise NotImplementedError('%d paths found in %s'%(len(path), line))
        ## The filename must be a number
        image_id = get_filename_as_int(filename)
        size = get_and_check(root, 'size', 1)
        # LiH 2019
        # If get(root, 'object') returns []
        # it means that the xml file doesn't have object
        # so don't use this xml to create json
        if len(get(root, 'object')) is 0:
            with open(os.path.join(os.path.dirname(xml_list),'except.txt'),'a+') as file:
                file.write(filename)
                file.write('\n')
            continue
        # print(get(root,'object'))

        width = int(get_and_check(size, 'width', 1).text)
        height = int(get_and_check(size, 'height', 1).text)
        image = {'file_name': filename, 'height': height, 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        for obj in get(root, 'object'):
            category = get_and_check(obj, 'name', 1).text
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = int(get_and_check(bndbox, 'xmin', 1).text) - 1
            ymin = int(get_and_check(bndbox, 'ymin', 1).text) - 1
            xmax = int(get_and_check(bndbox, 'xmax', 1).text) - 1
            ymax = int(get_and_check(bndbox, 'ymax', 1).text) - 1
            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            ann = {'area': o_width*o_height, 'iscrowd': 0, 'image_id':
                   image_id, 'bbox':[xmin, ymin, o_width, o_height],
                   'category_id': category_id, 'id': bnd_id, 'ignore': 0,
                   'segmentation': []}
            json_dict['annotations'].append(ann)
            bnd_id = bnd_id + 1

    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()
    list_fp.close()
    print(json_file," saved")

def create_xml_list(xml_path, xml_list_path):
    file_name = []
    xml_path = pathlib.Path(xml_path)
    for i in xml_path.iterdir():
        if i.is_file():
            file_name.append(i.name)
            print(i.name)
    with open(xml_list_path,'w+')as f:
        for tmp in file_name:
            f.write(tmp+'\n')
    return xml_list_path



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--xml_path',default='/home/lih/MarkerDataset/annotations',
                        help='path to pascal voc format xml list')
    parser.add_argument('--xml_list_path',default='/home/lih/MarkerDataset/xmllist.txt',
                        help='Path/to/a/txt/file, from xml path to create xmllist.txt')
    parser.add_argument('--output_path',default='/home/lih/MarkerDataset/coco_output.json',
                        help='Path/to/coco_format/outputfile')
    # parser.add_argument('--xml_path',default='/media/lih/LiH/DatasetToCheck/annotations1',
    #                     help='path to pascal voc format xml list')
    # parser.add_argument('--xml_list_path',default='//media/lih/LiH/DatasetToCheck/xmllist1.txt',
    #                     help='Path/to/a/txt/file, from xml path to create xmllist.txt')
    # parser.add_argument('--output_path',default='/media/lih/LiH/DatasetToCheck/coco_output.json',
    #                     help='Path/to/coco_format/outputfile')
    args = parser.parse_args()
    xml_list_path = create_xml_list(args.xml_path, args.xml_list_path)
    # convert(sys.argv[1], sys.argv[2], sys.argv[3])
    convert(xml_list_path, args.xml_path, args.output_path)