# based on https://github.com/facebookresearch/detectron2
import glob
import multiprocessing as mp
import os
import time
import cv2
import tqdm
from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from predictor import ObjectDetect

# constants
config_file = "mask_rcnn_R_50_FPN_3x.yaml"
model_weights = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"
confidence_threshold = 0.5 #confidence-threshold

cfg = get_cfg()
cfg.merge_from_file(config_file)
cfg.MODEL.WEIGHTS = model_weights
# Set score_threshold for builtin models
cfg.MODEL.RETINANET.SCORE_THRESH_TEST = confidence_threshold
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = confidence_threshold
cfg.freeze()
image = ["living-room.jpg"]
output = None
visualise = True # show gui of map

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    detect = ObjectDetect(cfg)


    if len(image) == 1:
        input = glob.glob(os.path.expanduser(image[0]))
        assert image, "The input path(s) was not found"
    for path in tqdm.tqdm(image, disable=not output):
        # use PIL, to be consistent with evaluation
        img = read_image(path, format="BGR")
        start_time = time.time()
        predictions, visualized_output = detect.run_on_image(img)
        print(
            "{}: {} in {:.2f}s".format(
                path,
                "detected {} instances".format(len(predictions["instances"]))
                if "instances" in predictions
                else "finished",
                time.time() - start_time,
            )
        )
        print(predictions["instances"])
        # tell me what you see
        #path to the left I see
        # Streight ahead i see
        # to the right i see

        if output:
            if os.path.isdir(output):
                assert os.path.isdir(output), output
                out_filename = os.path.join(output, os.path.basename(path))
            else:
                assert len(image) == 1, "Please specify a directory 'output'"
                out_filename = output
            visualized_output.save(out_filename)
        
        if visualise:
            cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
            cv2.imshow("Result", visualized_output.get_image()[:, :, ::-1])
            if cv2.waitKey(0) == 27:
                break  # esc to quit