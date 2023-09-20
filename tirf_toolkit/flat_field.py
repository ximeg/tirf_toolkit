import numpy as np
from math import ceil
from skimage.transform import resize


def get_flat_frame(stack, M = 8):
    """
    Calculate a flat-field frame to compensate for uneven illumination in the optical path.
    Subtraction of the flat-field frame results in more accurate image thresholding for
    particle detection, especially with uneven illumination profile.

    The function splits the image into MxM sized tiles, and takes one single pixel representing
    the 10-th intensity percentile from each tile to build a low-resolution flat-field image.
    After that, the flat-field image is scaled up to the size of the original image.
    """
    stack = np.asarray(stack)
    H, W = stack.shape[-2:]

    # If stack has multiple frames, extract up to 10 frames from it and average them
    if stack.ndim == 3:
        n = np.max([stack.shape[0], 10])
        stack = stack[::n // 10][:10].mean(axis = 0)

    tiles = [stack[..., y:y+M, x:x+M]
                for y in range(0, H, M)
                for x in range(0, W, M)]
    return resize(np.array([np.quantile(tile, 0.1) for tile in tiles]).\
                   reshape(ceil(H/M), ceil(W/M)),
                  (H, W), anti_aliasing=True)
