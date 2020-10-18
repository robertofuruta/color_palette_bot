"""
This module generates a color palette of num_colors colors from a provided image at input_file.
It saves it in the output_file and returns the list of strings of colors in hex.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib.colors import LinearSegmentedColormap
from scipy import cluster

import colorsys


# partitions is the number of samples of color to collect in each axis.
def color_palette_from_photo(input_file, output_file, num_colors=4, partitions=200, hsv=True):
    img = plt.imread(input_file)
    scale = 1
    if isinstance(img[0][0][0], np.floating):
        scale = 255
    # np_image is a flattened (partitions x partitions) array of colors, with three cols: r, g, b
    np_image = np.empty((partitions*partitions, 3), int)
    height = len(img[0])
    width = len(img)

    for i in range(partitions):
        for j in range(partitions):
            np_image[i*partitions+j,
                     :] = np.array(img[int(width/partitions*i)][int(height/partitions*j)])[:3]*scale

    if hsv:
        hsv_image = np.zeros_like(np_image, dtype=np.float)
        for i in range(partitions):
            for j in range(partitions):
                r, g, b = np_image[i*partitions+j, :].tolist()
                # print(r, g, b)
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                # print(h, s, v)
                hsv_image[i*partitions+j, :] = np.array([h, s, v])
        np_image = (hsv_image)

    color_palette = cluster.vq.kmeans(
        cluster.vq.whiten(np_image), num_colors)[0]  # this divides by the std

    rgb_std = np_image.std(axis=0)
    for i in range(num_colors):
        # this multiplies back the std
        color_palette[i, :] = rgb_std*color_palette[i]

    if hsv:
        rgb_color_palette = np.zeros_like(color_palette, dtype=int)
        for i in range(num_colors):
            h, s, v = color_palette[i, :].tolist()
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            rgb_color_palette[i, :] = np.array([r, g, b])
        color_palette = rgb_color_palette

    # resort in order of value
    summed = np.sum(color_palette, axis=1)
    ind = np.argsort(summed)
    color_palette = np.take(color_palette, ind, axis=0)

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    cm = LinearSegmentedColormap.from_list(
        'color color_palette', color_palette/255, num_colors)
    fig, ax = plt.subplots(nrows=1)
    dpi = 200
    fig.set_size_inches(num_colors, 1)
    ax.imshow(gradient, aspect='auto', cmap=(cm))
    ax.set_axis_off()

    plt.savefig(output_file, dpi=dpi)
    plt.close()

    imgs = [PIL.Image.open(input_file), PIL.Image.open(output_file)]
    print(imgs[0].size)
    new_w = imgs[0].size[1]

    resized = []
    for i in imgs:
        w, h = i.size
        new_h = int(new_w*h/w)
        resized.append(i.resize([new_w, new_h]))
    imgs_comb = np.vstack(resized)

    imgs_comb = PIL.Image.fromarray(imgs_comb)
    imgs_comb.save(output_file,)

    hex_colors = []
    for color in color_palette:
        hex_colors.append("#{0:02x}{1:02x}{2:02x}".format(
            *color.astype(int).tolist()))

    return hex_colors


def main():
    input_file = 'universe.jpg'
    output_file = 'out_universe.jpg'

    print(color_palette_from_photo(input_file,
                                   output_file, num_colors=5, partitions=200))


if __name__ == '__main__':
    main()
