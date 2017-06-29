#import DiffScreenshot
from PIL import Image, ImageDraw
from math import sqrt
import urllib, cStringIO
#import pymsgbox


def load_image(image_path):
    fle = cStringIO.StringIO(urllib.urlopen(image_path).read())
    image = Image.open(fle)
    width, height = image.size

    return image, width, height


def count_pixels(image, x0, y0, x1, y1):
    pixels = {}

    for coordinate_x in range(x0, x0+x1):
        for coordinate_y in range(y0, y0+y1):
            pixel = image.getpixel((coordinate_x, coordinate_y))


            try:
                pixels['(' + str(pixel[0]) + ',' + str(pixel[1])+ ',' + str(pixel[2]) + ')'] += 1
            except KeyError:
                pixels['(' + str(pixel[0]) + ',' + str(pixel[1]) + ',' + str(pixel[2]) + ')'] = 1

    return pixels




def number_of_pixels_within_range(pixels_dict, wanted_color, tolerance=0):
    number = 0

    for key in pixels_dict.keys():
        rgb = eval(key)

        diff = sqrt((wanted_color[0] - rgb[0])**2 + (wanted_color[1] - rgb[1])**2 + (wanted_color[2] - rgb[2]) **2)
        if diff <= tolerance:
            number += pixels_dict[key]

    return number




def count_pixels_with_tolerance(pixels_dict, tolerance=0):
    pixels_dict_tolerance = {}

    for key in pixels_dict.keys():
        rgb = eval(key)
        pixels_dict_tolerance[key] = number_of_pixels_within_range(pixels_dict, rgb, tolerance)

    return pixels_dict_tolerance




def number_of_pixels_percent(pixels_dict):
    percentages = {}
    sum_val = sum(pixels_dict.values())
    for key in pixels_dict.keys():
        value = pixels_dict[key]
        perc = float(value) / float(sum_val) * 100
        percentages[key] = round(perc, 2)

    return percentages



def check_percentage_equal_to(image_path, start_x, start_y, size_x, size_y, rgb, tolerance, percentage):
    """
    :param image_path: the path of the image to analyze, you want it to be the url of bucket
    :param start_x: x coordinate of the top_left corner of the region to analyze
    :param start_y: y coordinate of the top_left corner of the region to analyze
    :param size_x: width of the region
    :param size_y: height of the region
    :param rgb: a tuple (int, int, int) or a string "(int,int,int)" - in the json file this is a list, needs to be converted to a tuple
    :param tolerance: a number indicating the variability of the given color
    :param percentage: the function returns true if the percentage of the color in the region matches this number
            the percentage is in the format xx.x% - tolerance +-0.3%
    :return: True if the found percentage is equal to the given percentage, the actual percentage otherwise
    """


    image_path = str(image_path); start_x = int(start_x); start_y = int(start_y); size_x = int(size_x); size_y = int(size_y)
    rgb = eval(str(rgb)); tolerance = int(tolerance); percentage = float(percentage)


    image, width, height = load_image(str(image_path))

    box = (start_x, start_y, start_x + size_x, start_y + size_y)

    region = image.crop(box)

    width, height = region.size


    area = width * height

    pixels_dict = count_pixels(region, 0, 0, size_x, size_y)

    #print(sum(pixels_dict.values()))
    #print(area)
    n_pix = number_of_pixels_within_range(pixels_dict, rgb, tolerance)

    #highlight_pixels_within_range(region, rgb, tolerance)

    #region.show()
    #print(n_pix)

    #pymsgbox.alert('area: ' + str(area) + '\nn_pix: ' + str(n_pix) + '\nperc: ' + str(percentage))

    if round(float(n_pix)/float(area) * 100, 2) >= percentage - 0.3 and round(float(n_pix)/float(area) * 100, 2) <= percentage + 0.3:
        return True
    else:
        return str(round(float(n_pix)/float(area) * 100, 2))



def highlight_pixels_within_range(image, color, tol):
    width, height = image.size
    color = eval(color)

    for coordinate_X in range(0, width):
        for coordinate_Y in range(0, height):
            pixel = image.getpixel((coordinate_X, coordinate_Y))

            diff = sqrt(
                (color[0] - pixel[0]) ** 2 + (color[1] - pixel[1]) ** 2 + (color[2] - pixel[2]) ** 2)

            if diff <= tol:
                image.putpixel((coordinate_X, coordinate_Y), (100,240,255))



if __name__ == '__main__':
    # image, width, height = load_image('test red.png')
    # pixels_dict = count_pixels(image, 0, 0, width, height)
    #print(number_of_pixels_within_range(pixels_dict, (255, 0, 0), 10))
    # print('dictionary', pixels_dict)
    # print('with tolerance', count_pixels_with_tolerance(count_pixels(image, 0, 0, width, height), 100))
    # print('percent', number_of_pixels_percent(pixels_dict))
    # print('close to red', number_of_pixels_within_range(pixels_dict, (255,95,83), 200))
    '''for x in range(900, 2901, 1000):
        for y in range(515, 1316, 400):

            if x == 2900 and y == 1315:
                rgb = '(64,249,97)'
            else:
                rgb = '(255,95,83)'
'''
    print(check_percentage_equal_to('https://a360ci.s3.amazonaws.com/difftool/screenshots/test/test_720.png',  0,  0, 250, 250, '(250,53,85)',  120,  8.3))
