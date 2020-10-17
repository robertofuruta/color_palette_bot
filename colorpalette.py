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


# partitions is the number of samples of color to collect in each axis.
def color_palette_from_photo(input_file, output_file, num_colors=4, partitions=100):
    img = plt.imread(input_file)
    scale = 1
    if isinstance(img[0][0][0], np.floating):
        scale = 255
    # np_image is a flattened (partitions x partitions) array of colors, with three cols: r, g, b
    np_image = np.empty((partitions*partitions, 3), int)
    height = len(img)
    width = len(img[0])

    for i in range(partitions):
        for j in range(partitions):
            np_image[i*100+j,
                     :] = np.array(img[int(height/100*i)][int(width/100*j)])[:3]*scale

    color_palette = cluster.vq.kmeans(
        cluster.vq.whiten(np_image), num_colors)[0]  # this divides by the std

    rgb_std = np_image.std(axis=0)
    for i in range(num_colors):
        # this multiplies back the std
        color_palette[i, :] = rgb_std*color_palette[i]

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    cm = LinearSegmentedColormap.from_list(
        'color color_palette', color_palette/255, num_colors)
    fig, ax = plt.subplots(nrows=1)
    dpi = 64
    fig.set_size_inches(width/dpi, 1*width/dpi/num_colors)
    ax.imshow(gradient, aspect='auto', cmap=(cm))
    ax.set_axis_off()

    plt.savefig(output_file, dpi=dpi)
    plt.close()

    imgs = [PIL.Image.open(input_file), PIL.Image.open(output_file)]
    # min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.vstack(
        (np.asarray(i.resize([imgs[0].size[0], i.size[1]])) for i in imgs))
    # imgs_comb = np.vstack(np.asarray(img) for img in imgs)
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    imgs_comb.save(output_file)

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
    main()
