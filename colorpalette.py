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
from scipy.stats import norm
# from scipy.signal import gaussian
# import math

import colorsys


def gaussian(array, mu, sig):
    return (sig*2*np.pi)**-0.5*np.exp(-(array - mu)**2 / (2 * sig**2))


def inv_gaussian(array, mu, sig):
    return mu - sig*np.sqrt(2*np.log(1/(sig*array)) - np.log(2*np.pi))


def color_palette_from_photo(input_file, output_file, num_colors=5, partitions=150, hsv=True, envelop=False, select=True, individual=True):
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
                r, g, b = (np_image[i*partitions+j, :]/255).tolist()

                h, s, v = colorsys.rgb_to_hsv(r, g, b)

                hsv_image[i*partitions+j, :] = np.array([h, s, v])
        np_image = hsv_image

    if select:

        color_palette = cluster.vq.kmeans(
            cluster.vq.whiten(np_image), 2*num_colors)[0]  # this divides by the std

        if individual:
            # individual_score = color_palette[:, 1] *\
            #     color_palette[:, 2]*gaussian(color_palette[:, 2], np.mean(
            #         color_palette[:, 2]), np.std(color_palette[:, 2])/2)
            individual_score = np.sqrt(np.absolute(color_palette[:, 0]-np.mean(color_palette[:, 0]))) *\
                np.power(color_palette[:, 1], 2) *\
                color_palette[:, 2]/np.mean(color_palette[:, 2])

            indexes = np.argsort(individual_score)
            color_palette = np.take(color_palette, indexes, axis=0)[
                num_colors:]

        else:
            def weighted_sum(tripple, a=2, b=4, c=1, mu=0.8, sig=.2):
                return a*tripple[0]+b*tripple[1]*gaussian(tripple[1], mu, sig)+c*tripple[2]*gaussian(tripple[2], mu, sig)

            color_difference = np.zeros((2*num_colors, 2*num_colors))
            for i in range(2*num_colors):
                for j in range(2*num_colors):
                    color_difference[i, j] = weighted_sum(
                        color_palette[i]-color_palette[j])
            indexes = [int(np.argmax(np.sum(color_difference, axis=0)))]
            new_color_palette = np.empty((num_colors, 3))
            new_color_palette[0, :] = color_palette[indexes[-1], :]
            stacked_differences = np.zeros(2*num_colors)
            stacked_differences[:] = color_difference[indexes[-1], :]
            for i in range(num_colors-1):
                ind_sort = np.argsort(stacked_differences)
                for k in range(len(indexes)+1):
                    unique_max = 2*num_colors-1-i-k
                    for j in range(2*num_colors):
                        if ind_sort[j] == unique_max:
                            if j not in indexes:
                                indexes.append(j)
                                break
                    if len(indexes) == i+2:
                        break
                new_color_palette[i+1, :] = color_palette[indexes[-1], :]
                stacked_differences[:] = stacked_differences[:] + \
                    color_difference[indexes[-1], :]
            color_palette = new_color_palette

    else:
        color_palette = cluster.vq.kmeans(
            cluster.vq.whiten(np_image), num_colors)[0]  # this divides by the std

    rgb_std = np_image.std(axis=0)
    for i in range(num_colors):
        # this multiplies back the std
        color_palette[i, :] = rgb_std*color_palette[i]

    if hsv:
        if envelop:
            get_envelop(color_palette, inv=True)

        rgb_color_palette = np.zeros_like(color_palette, dtype=int)
        for i in range(num_colors):
            h, s, v = color_palette[i, :].tolist()
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            rgb_color_palette[i, :] = np.array([r, g, b])*255
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
                                   output_file))


if __name__ == '__main__':
    main()
