import argparse
import yaml
import shutil
import os
import subprocess

import sys

from tqdm import tqdm
from loguru import logger
from yaml import load
from yaml import FullLoader

def split_data(name_dir, datapath):
    # Create train, test and validation dataset
    try:
        os.mkdir(f'{name_dir}/dataset')
        os.mkdir(f'{name_dir}/dataset/train')
        os.mkdir(f'{name_dir}/dataset/test')
        os.mkdir(f'{name_dir}/dataset/val')

    except Exception:
        logger.exception('Directory with split dataset already exist')

    train_size = int(0.6 * len(os.listdir(datapath)))
    val_size = int(0.35 * len(os.listdir(datapath)))
    test_size = int(0.05 * len(os.listdir(datapath)))
    count = 0
    for data in tqdm(os.listdir(datapath)):
        if count < train_size:
            shutil.copy(datapath + '/' + data, f'{name_dir}/dataset/train')
            count += 1
        if count >= train_size and count < train_size + val_size:
            shutil.copy(datapath + '/' + data, f'{name_dir}/dataset/val')
            count += 1
        if count > train_size and count >= train_size + val_size:
            shutil.copy(datapath + '/' + data, f'{name_dir}/dataset/test')
            count += 1

    logger.info('Count of train example: ' + str(train_size))
    logger.info('Count of val example: ' + str(val_size))
    logger.info("Count of test example: " + str(test_size))

def create_class_list(filename):
    #Returns list of class
    file = open(filename, "r")
    class_list = file.read().splitlines()
    file.close()
    return class_list


def create_config_data(train_path, val_path, classname_file, config_path):
    # Create data config
    logger.info('Create config file')
    class_list = create_class_list(classname_file)
    data = dict(train=train_path,
                val=val_path,
                nc=len(class_list),
                names=class_list
                )
    with open(config_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


def load_config(config_file):
    # Returns loaded config сhosen architecture
    with open(config_file) as f:
        return load(f, Loader=FullLoader)

def train_V5(DATA_PATH ,IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, SAVE_PATH, SPLIT):
    """
    Runs yolov5 training using the parameters specified in the config.

    :param DATA_PATH: Path to save split dataset.
    :param IMG_SIZE: Size of input images as integer or w,h.
    :param BATCH_SIZE: Batch size for training.
    :param EPOCHS: Number of epochs to train for.
    :param CONFIG_PATH: Path to config dataset.
    :param MODEL_PATH: Path to model file (yaml).
    :param SAVE_PATH: Path to save model.pt.
    :param SPLIT: Split dataset (True/False).
    """
    if SPLIT:
        split_data('yolov5', DATA_PATH)
    os.system(
        f'OMP_NUM_THREADS=1 python -m torch.distributed.run --nproc_per_node 5 yolov5/train.py --img ' +
        IMG_SIZE +
        ' --batch ' +
        BATCH_SIZE +
        ' --epochs ' +
        EPOCHS +
        ' --data ' +
        CONFIG_PATH +
        ' --cfg ' +
        MODEL_PATH +
        ' --weights ' +
        SAVE_PATH + ' --device 0,1,2,3,4')

    
def train_V7(DATA_PATH ,IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, SPLIT):
    """
    Runs yolov7 training using the parameters specified in the config.

    :param DATA_PATH: Path to save split dataset.
    :param IMG_SIZE: Size of input images as integer or w,h.
    :param BATCH_SIZE: Batch size for training.
    :param EPOCHS: Number of epochs to train for.
    :param CONFIG_PATH: Path to config dataset.
    :param MODEL_PATH: Path to model file (yaml).
    :param SPLIT: Split dataset (True/False).
    """
    if SPLIT:
        split_data('yolov7', DATA_PATH)
    os.system('OMP_NUM_THREADS=1 python3 -m torch.distributed.launch --nproc_per_node 5 yolov7/train.py'
    ' --device 0,1,2,3,4' +
    ' --batch-size ' +
    BATCH_SIZE +
    ' --data ' +
    CONFIG_PATH +
    ' --img ' +
    IMG_SIZE +
    ' --cfg ' +
    MODEL_PATH +
    ' --epochs '+
    EPOCHS +
    ' --name run'+
    " --weights ''")


def train_V8(DATA_PATH ,IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, SPLIT):
    """
    Runs yolov8 training using the parameters specified in the config.

    :param DATA_PATH: Path to save split dataset.
    :param IMG_SIZE: Size of input images as integer or w,h.
    :param BATCH_SIZE: Batch size for training.
    :param MODEL_PATH: Path to model file (yaml).
    :param EPOCHS: Number of epochs to train for.
    :param SPLIT: Split dataset (True/False).
    :param CONFIG_PATH: Path to config dataset.
    """
    if SPLIT:
        split_data('ultralytics', DATA_PATH)

    os.system(f'yolo detect train data=' +
    CONFIG_PATH +
    ' imgsz=' +
    IMG_SIZE +
    ' batch=' +
    BATCH_SIZE +
    ' epochs=' +
    EPOCHS +
    ' model='+
    MODEL_PATH +
    ' device=0,1,2,3,4'
    )
   

def run(arch, split):
    """
    Create config, run learning functions and split dataset if you need it.  

    :param arhc: Trainable architecture.
    :param split: Creating train and validation dataset.
    """
    if arch == "yolov5":
        config = load_config('config/custom_config_v5.yaml')
    elif arch == "yolov8":
        config = load_config('config/custom_config_v8.yaml')
    else:
        config = load_config('config/custom_config_v7.yaml')

    DATA_PATH = config['DATA_PATH']
    CLASSES = config['CLASSES']
    IMG_SIZE = config['IMG_SIZE']
    BATCH_SIZE = config['BATCH_SIZE']
    EPOCHS = config['EPOCHS']
    CONFIG_PATH = config['CONFIG_PATH']
    MODEL_PATH = config['MODEL_PATH']
    SAVE_PATH = config['SAVE_PATH']
    #MODEL_NAME = config['MODEL_NAME']

    if arch == 'yolov8':
        create_config_data('/media/farm/ssd_1_tb_evo_sumsung/train_yolo_utils/ultralytics/dataset/train', '/media/farm/ssd_1_tb_evo_sumsung/train_yolo_utils/ultralytics/dataset/val', CLASSES, CONFIG_PATH)
        train_V8(DATA_PATH, IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, split)
    elif arch == 'yolov5':
        create_config_data('dataset/train', 'dataset/val', CLASSES, CONFIG_PATH)
        train_V5(DATA_PATH, IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, SAVE_PATH, split)
    elif arch == 'yolov7':
        create_config_data('yolov7/dataset/train', 'yolov7/dataset/val', CLASSES, CONFIG_PATH)
        train_V7(DATA_PATH, IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, split)
    

def parse_opt():
    parser =  argparse.ArgumentParser()
    parser.add_argument('--arch', type=str, default='yolov8')
    parser.add_argument('--split', type=bool, default=False)
    opt = parser.parse_args()
    return opt



if __name__ == "__main__":
    opt = parse_opt()
    run(**vars(opt))