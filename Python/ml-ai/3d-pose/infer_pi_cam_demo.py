import io
import socket
import struct
import cv2
from PIL import Image
import time

from argparse import ArgumentParser
import json
import os

import cv2
import numpy as np

from modules.input_reader import VideoReader, ImageReader
from modules.draw import Plotter3d, draw_poses
from modules.parse_poses import parse_poses
from modules.inference_engine_pytorch import InferenceEnginePyTorch

#3d pose estimation

model = "/home/ubuntu/rexana/ml-ai/3d-pose/models/human-pose-estimation-3d.pth"
device = "GPU" # "GPU" or "CPU" 
file_path = os.path.join('data', 'extrinsics.json')
net = InferenceEnginePyTorch(model, device)
use_video = False # process images from video or images
test_image = ["/home/ubuntu/rexana/ml-ai/3d-pose/test-media/jumping_jack.jpg"]
canvas_3d = np.zeros((720, 1280, 3), dtype=np.uint8)
plotter = Plotter3d(canvas_3d.shape[:2])
canvas_3d_window_name = 'Canvas 3D'
cv2.namedWindow(canvas_3d_window_name)
cv2.setMouseCallback(canvas_3d_window_name, Plotter3d.mouse_callback)


def rotate_poses(poses_3d, R, t):
    R_inv = np.linalg.inv(R)
    for pose_id in range(len(poses_3d)):
        pose_3d = poses_3d[pose_id].reshape((-1, 4)).transpose()
        pose_3d[0:3, :] = np.dot(R_inv, pose_3d[0:3, :] - t)
        poses_3d[pose_id] = pose_3d.transpose().reshape(-1)

    return poses_3d

def pose_estimation(image):
    with open(file_path, 'r') as f:
      extrinsics = json.load(f)
    
    R = np.array(extrinsics['R'], dtype=np.float32)
    t = np.array(extrinsics['t'], dtype=np.float32)

    is_video = True
    if use_video:
        frame_provider = VideoReader(video)
        is_video = True
    else:
        frame_provider = ImageReader(image)    
    
    base_height = 256 # Network input layer size
    fx =  -1  # camera focal length
    stride = 8

    delay = 1
    esc_code = 27
    p_code = 112
    space_code = 32
    mean_time = 0
    
    for frame in frame_provider:
        current_time = cv2.getTickCount()
        if frame is None:
            break
        input_scale = base_height / frame.shape[0]
        scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
        scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
        if fx < 0:  # Focal length is unknown
            fx = np.float32(0.8 * frame.shape[1])

        inference_result = net.infer(scaled_img)
        poses_3d, poses_2d = parse_poses(inference_result, input_scale, stride, fx, is_video)
        edges = []
        if len(poses_3d):
            poses_3d = rotate_poses(poses_3d, R, t)
            poses_3d_copy = poses_3d.copy()
            x = poses_3d_copy[:, 0::4]
            y = poses_3d_copy[:, 1::4]
            z = poses_3d_copy[:, 2::4]
            poses_3d[:, 0::4], poses_3d[:, 1::4], poses_3d[:, 2::4] = -z, x, -y

            poses_3d = poses_3d.reshape(poses_3d.shape[0], 19, -1)[:, :, 0:3]
            edges = (Plotter3d.SKELETON_EDGES + 19 * np.arange(poses_3d.shape[0]).reshape((-1, 1, 1))).reshape((-1, 2))
        plotter.plot(canvas_3d, poses_3d, edges)
        cv2.imshow(canvas_3d_window_name, canvas_3d)

        draw_poses(frame, poses_2d)
        current_time = (cv2.getTickCount() - current_time) / cv2.getTickFrequency()
        if mean_time == 0:
            mean_time = current_time
        else:
            mean_time = mean_time * 0.95 + current_time * 0.05
        cv2.putText(frame, 'FPS: {}'.format(int(1 / mean_time * 10) / 10),
                    (40, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
        cv2.imshow('ICV 3D Human Pose Estimation', frame)

        key = cv2.waitKey(delay)
        if key == esc_code:
            break
        if key == p_code:
            if delay == 1:
                delay = 0
            else:
                delay = 1
        if delay == 0 or not is_video:  # allow to rotate 3D canvas while on pause
            key = 0
            while (key != p_code
                   and key != esc_code
                   and key != space_code):
                plotter.plot(canvas_3d, poses_3d, edges)
                cv2.imshow(canvas_3d_window_name, canvas_3d)
                key = cv2.waitKey(33)
            if key == esc_code:
                break
            else:
                delay = 1

# test single image
# pose_estimation(test_image)

# Start a socket listening for connections (raspwberry pi client will send video data over socket 
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 5656))
server_socket.listen(0)
print("Listening for video stream")

# Accept connection and make a "file" object
connection = server_socket.accept()[0].makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        print('Image is %dx%d' % image.size)
        #image.verify()
        print('Image is verified')
        # test processing using opencv (change to greyscale)
        print("Process image using opencv")
        cvImg = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        filename = "data/video_frames/pi_image-%s.jpg" %(int(time.time()))
        cv2.imwrite(filename, cvImg)
        print("Wait for image to write")
        pose_estimation([filename])
        
finally:
    connection.close()
    server_socket.close()
