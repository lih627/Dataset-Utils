import glob
import pathlib
from shutil import copyfile
import os
import cv2
import os.path as osp
import sys
from lxml.etree import Element, SubElement, tostring, parse
from xml.dom.minidom import parseString
import time
from math import ceil

def TransformDataset(anno_path = '/media/lih/LiH/LRDataset/annotations',
                     img_path = '/media/lih/LiH/LRDataset/images',
                     anno_save_path = '/media/lih/LiH/LRDataset/lrannotations',
                     img_save_path = '/media/lih/LiH/LRDataset/lrimages'
                     ):
    '''
    :param anno_path: annotations path
    :param img_path:  images path
    :param anno_save_path:  anmnotations save path, chang xml params to match resized imgs
    :param img_save_path:  images save path, resized image to [0.5h 0.5w]
    :return:
    '''
    anno_name = []
    for root, subdirs, files in os.walk(anno_path):
        for filepath in files:
            anno_name.append(filepath)
    img_name = []
    for root, subdirs, files in os.walk(img_path):
        for filepath in files:
            img_name.append(filepath)
    # read img, resize and save
    for tmp in img_name:
        curr_img = cv2.imread(osp.join(img_path,tmp))
        print("Process {}".format(tmp))
        assert curr_img.shape == (720, 1280, 3)
        curr_img = cv2.resize(curr_img,(640, 360))
        # cv2.imshow('debug', curr_img)
        # cv2.waitKey(1)
        assert curr_img.shape == (360,  640, 3)
        cv2.imwrite(osp.join(img_save_path,tmp), curr_img)
    # process xml
    for tmp in anno_name:
        xml_f = osp.join(anno_path, tmp)
        tree = parse(xml_f)

        node_root = Element('annotation')
        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'images'
        node_filename = SubElement(node_root, 'filename')

        node_filename.text = tree.xpath('//filename/text()')[0]
        node_path = SubElement(node_root, 'path')
        node_path.text = tree.xpath('//path/text()')[0]
        node_source = SubElement(node_root, 'source')
        node_database = SubElement(node_source, 'database')
        node_database.text = 'Unknown'

        node_size = SubElement(node_root, 'size')
        node_width = SubElement(node_size, 'width')
        node_width.text = str(int(int(tree.xpath('//width/text()')[0])/2))

        node_height = SubElement(node_size, 'height')
        node_height.text = str(int(int(tree.xpath('//height/text()')[0])/2))

        node_depth = SubElement(node_size, 'depth')
        node_depth.text = tree.xpath('//depth/text()')[0]

        node_segmented = SubElement(node_root, 'segmented')
        node_segmented.text = '0'

        for num in range(len(tree.xpath('//name/text()'))):
            xmin = tree.xpath('//xmin/text()')
            ymin = tree.xpath('//ymin/text()')
            xmax = tree.xpath('//xmax/text()')
            ymax = tree.xpath('//ymax/text()')
            node_object = SubElement(node_root, 'object')
            node_name = SubElement(node_object, 'name')
            node_name.text = 'marker'
            node_pose = SubElement(node_object, 'pose')
            node_pose.text = 'Unspecified'
            node_truncated = SubElement(node_object, 'truncated')
            node_truncated.text = '0'
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = str(ceil(0.5*int(xmin[num])))
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = str(ceil(0.5*int(ymin[num])))
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = str(ceil(0.5*int(xmax[num])))
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = str(ceil(0.5*int(ymax[num])))

        xml = tostring(node_root, pretty_print=True)  # 格式化显示，该换行的换行
        xml_file_path = os.path.join(anno_save_path, tmp)
        print(xml_file_path)
        with open(xml_file_path, 'wb') as file:
            file.write(xml)





if __name__=='__main__':
    TransformDataset()
