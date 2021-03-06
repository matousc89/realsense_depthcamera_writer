# First import the library
import pyrealsense2 as rs
import numpy as np
import cv2
import time

X_RGB = X_DEPTH = 1280
Y_RGB = 800
Y_DEPTH = 720

X_CANVAS = X_DEPTH
Y_CANVAS = 2 * Y_RGB #+ Y_DEPTH


canvas = np.zeros((Y_CANVAS, X_CANVAS, 3), dtype="uint8")

writer = cv2.VideoWriter("video.avi", cv2.VideoWriter_fourcc(*"MJPG"), 15, (X_CANVAS, Y_CANVAS))


try:
    pipeline = rs.pipeline()

    # Configure streams
    config = rs.config()
    config.enable_stream(rs.stream.color, X_RGB, Y_RGB, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, X_DEPTH, Y_DEPTH, rs.format.z16, 30)

    pipeline.start(config)
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)
    dec_filter = rs.decimation_filter()
    temp_filter = rs.temporal_filter()
    spat_filter = rs.spatial_filter()

    align_to = rs.stream.color
    align = rs.align(align_to)

    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame: continue


        depth_frame = depth_to_disparity.process(depth_frame)
        depth_frame = dec_filter.process(depth_frame)
        depth_frame = temp_filter.process(depth_frame)
        depth_frame = spat_filter.process(depth_frame)
        depth_frame = disparity_to_depth.process(depth_frame)
        depth_frame = depth_frame.as_depth_frame()


        depth_data = depth_frame.as_frame().get_data()
        rgb_data = color_frame.as_frame().get_data()

        rgb_image = np.asanyarray(rgb_data)
        depth_image = np.asanyarray(depth_data)
        #depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        #print(depth_image.min(), depth_image.max())

        canvas[0:Y_RGB, :] = rgb_image
        canvas[Y_RGB:, :, 0] = depth_image // 256
        canvas[Y_RGB:, :, 1] = depth_image % 256
        writer.write(canvas)

        cv2.imshow("canvas", canvas)


        #cv2.imshow("depth", np.clip(depth_image, 0, 20000) * 6.5 / 2)
        #cv2.imshow("depth", depth_image*10 )



        # cv2.imshow('RGB', rgb_image)
        # cv2.imshow('depth', depth_image)


        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    exit(0)
except Exception as e:
    print(e)
    pass