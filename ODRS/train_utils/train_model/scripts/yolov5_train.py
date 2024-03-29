import os
from pathlib import Path

# def train_V5(IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, GPU_COUNT, SELECT_GPU):
#     opt = train.parse_opt()
#     opt.imgsz = IMG_SIZE
#     opt.batch_size = BATCH_SIZE
#     opt.epochs = EPOCHS
#     opt.data = CONFIG_PATH
#     opt.cfg = MODEL_PATH
#     opt.device = SELECT_GPU
#     opt.cache = True
#     opt.project = CONFIG_PATH.parent
#     opt.name = 'exp'
#     train.main(opt)


def train_V5(IMG_SIZE, BATCH_SIZE, EPOCHS, CONFIG_PATH, MODEL_PATH, GPU_COUNT, SELECT_GPU):
    """
    Runs yolov5 training using the parameters specified in the config.


    :param IMG_SIZE: Size of input images as integer or w,h.
    :param BATCH_SIZE: Batch size for training.
    :param EPOCHS: Number of epochs to train for.
    :param CONFIG_PATH: Path to config dataset.
    :param MODEL_PATH: Path to model file (yaml).
    :param GPU_COUNT: Number of video cards.
    """
    file = Path(__file__).resolve()
    command = "python3" if GPU_COUNT == 0 else f"OMP_NUM_THREADS=1 python3 -m torch.distributed.run --nproc_per_node {GPU_COUNT}"

    train_script_path = str(Path(file.parents[1]) / 'models' / 'yolov5' / 'train.py')

    full_command = (
        f"{command} {train_script_path}"
        f" --img {IMG_SIZE}"
        f" --batch {BATCH_SIZE}"
        f" --epochs {EPOCHS}"
        f" --data {CONFIG_PATH}"
        f" --cfg {MODEL_PATH}"
        f" --device {SELECT_GPU}"
        f" --project {CONFIG_PATH.parent}"
        f" --name exp"
    )
    os.system(full_command)
