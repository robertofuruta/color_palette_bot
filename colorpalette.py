
import os

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib.colors import LinearSegmentedColormap
from scipy import cluster

# import pandas as pd
# import math
# import colorsys
# import click


def color_palette_from_photo(input_file, output_file, num_colors=4, partitions=100):
    img = plt.imread(input_file)
    np_image = np.empty((partitions*partitions, 3), int)  # 2 dim: r, g, b
    height = len(img)
    width = len(img[0])

    for i in range(partitions):
        for j in range(partitions):
            np_image[i*100+j,
                     :] = np.array(img[int(height/100*i)][int(width/100*j)])

    color_palette = cluster.vq.kmeans(
        cluster.vq.whiten(np_image), num_colors)[0]

    rgb_std = np_image.std(axis=0)
    for i in range(num_colors):
        color_palette[i, :] = rgb_std*color_palette[i]

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    cm = LinearSegmentedColormap.from_list(
        'color color_palette', color_palette/255, num_colors)
    fig, ax = plt.subplots(nrows=1)
    fig.set_size_inches(num_colors, 1)
    ax.imshow(gradient, aspect='auto', cmap=(cm))
    ax.set_axis_off()

    plt.savefig(output_file, dpi=200)
    # plt.show()

    hex_colors = []
    for color in color_palette:
        hex_colors.append("#{0:02x}{1:02x}{2:02x}".format(
            *color.astype(int).tolist()))

    return hex_colors


def main():
    input_file = 'universe.jpg'
    output_file = 'out_universe.jpg'

    print(color_palette_from_photo(input_file,
                                   output_file, num_colors=4, partitions=100))


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    # input('test')
    main()
