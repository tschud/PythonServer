from PIL import Image, ImageDraw
from math import sqrt
import S3Uploader


class FailedMarkupCreation(RuntimeError):
    ROBOT_CONTINUE_ON_FAILURE = True


class Analyzer:

    def __init__(self, path, target_color=(255,255,255), top_left_x=0, top_left_y=0, bottom_right_x=-1, bottom_right_y=-1, tolerance=10, size_in_percentage=False):
        self.img = Image.open(path)
        self.tolerance = tolerance
        self.target_color = target_color
        self.width, self.height = self.img.size

        if size_in_percentage:
            if bottom_right_x == -1:
                bottom_right_x = 100
            if bottom_right_y == -1:
                bottom_right_y = 100

            self.top_left_x = int(self.width * top_left_x / 100)
            self.top_left_y = int(self.height * top_left_y / 100)
            self.bottom_right_x = int(self.width * bottom_right_x / 100)
            self.bottom_right_y = int(self.height * bottom_right_y / 100)
        else:
            if bottom_right_x == -1:
                bottom_right_x = self.width
            if bottom_right_y == -1:
                bottom_right_y = self.height

            self.top_left_x = top_left_x
            self.top_left_y = top_left_y
            self.bottom_right_x = bottom_right_x
            self.bottom_right_y = bottom_right_y

        self.region = self.img.crop((self.top_left_x, self.top_left_y, self.bottom_right_x, self.bottom_right_y))
        self.count_all_pixels_in_region()

    def count_all_pixels_in_region(self):
        self.pixels = {}

        for coordinate_x in range(self.top_left_x, self.bottom_right_x + 1):
            for coordinate_y in range(self.top_left_y, self.bottom_right_y + 1):
                pixel = self.img.getpixel((coordinate_x, coordinate_y))

                try:
                    self.pixels[str(tuple(pixel[:3]))] += 1
                except KeyError:
                    self.pixels[str(tuple(pixel[:3]))] = 1

        return self.pixels

    def count_similar_pixels(self):
        number = 0

        for key in self.pixels.keys():
            rgb = eval(key)

            diff = sqrt(
                (self.target_color[0] - rgb[0]) ** 2 + (self.target_color[1] - rgb[1]) ** 2 + (self.target_color[2] - rgb[2]) ** 2)
            if diff <= self.tolerance:
                number += self.pixels[key]

        return number

    def create_mask(self):
        for coordinate_X in range(self.top_left_x, self.bottom_right_x + 1):
            for coordinate_Y in range(self.top_left_y, self.bottom_right_y + 1):
                pixel = self.img.getpixel((coordinate_X, coordinate_Y))

                diff = sqrt((self.target_color[0] - pixel[0]) ** 2 + (self.target_color[1] - pixel[1]) ** 2 + (self.target_color[2] - pixel[2]) ** 2)

                if diff >= self.tolerance:
                    self.img.putpixel((coordinate_X, coordinate_Y), (0, 0, 0))

        draw = ImageDraw.Draw(self.img)
        for i in range(5):
            rect_start = (self.top_left_x - i, self.top_left_y - i)
            rect_end = (self.bottom_right_x + i, self.bottom_right_y + i)
            draw.rectangle((rect_start, rect_end), outline=(100, 240, 255))

    def perform_expected_percentage_check(self, expected_percentage, show_region=False, percentage_range=0.5):
        number_of_pixels = self.count_similar_pixels()

        if show_region:
            self.create_mask()
            self.img.show()

        percentage = round(float(number_of_pixels) / sum(self.pixels.values()) * 100, 2)

        if percentage >= expected_percentage - percentage_range and percentage <= expected_percentage + percentage_range:
            return True, percentage
        else:
            return False, percentage


class MultipleAnalysis:

    def __init__(self, tests_list):
        self.img = Image.open(tests_list["path"])
        self.tests_list = tests_list

    def run_multiple_tests(self, show_region=False):

        results = {}

        for case in self.tests_list["tests"]:
            analyser = Analyzer(
                path=self.tests_list["path"],
                target_color=case["target_color"],
                top_left_x=case["top_left_x"],
                top_left_y=case["top_left_y"],
                bottom_right_x=case["bottom_right_x"],
                bottom_right_y=case["bottom_right_y"],
                tolerance=case["tolerance"],
                size_in_percentage=case["size_in_percentage"]
            )

            results[case["name"]] = analyser.perform_expected_percentage_check(
                expected_percentage=case["expected_percentage"],
                show_region=False,
                percentage_range=case["percentage_range"]
            )

            if case["show_region"]:
                self.create_multiple_mask(
                    top_left_x=case["top_left_x"],
                    top_left_y=case["top_left_y"],
                    bottom_right_x=case["bottom_right_x"],
                    bottom_right_y=case["bottom_right_y"],
                    PIL_image=self.img,
                    target_color=case["target_color"],
                    tolerance=case["tolerance"]
                )

        if show_region:
            path = '/Users/administrator/Desktop/PythonServer/LocalUploads/markup_result.png'
            self.img.save(path, "PNG")
            url = S3Uploader.uploadOnly(path)
            return results, url

        return results

    def create_multiple_mask(self,top_left_x, top_left_y, bottom_right_x, bottom_right_y, PIL_image, target_color, tolerance):
        for coordinate_X in range(top_left_x, bottom_right_x + 1):
            for coordinate_Y in range(top_left_y, bottom_right_y + 1):
                pixel = PIL_image.getpixel((coordinate_X, coordinate_Y))

                diff = sqrt((target_color[0] - pixel[0]) ** 2 + (target_color[1] - pixel[1]) ** 2 + (target_color[2] - pixel[2]) ** 2)

                if diff >= tolerance:
                    PIL_image.putpixel((coordinate_X, coordinate_Y), (0, 0, 0))

        draw = ImageDraw.Draw(PIL_image)
        for i in range(5):
            rect_start = (top_left_x - i, top_left_y - i)
            rect_end = (bottom_right_x + i, bottom_right_y + i)
            draw.rectangle((rect_start, rect_end), outline=(100, 240, 255))


def set_image_for_multiple_tests(empty_dictionary, image_path):
    empty_dictionary["path"] = image_path
    empty_dictionary["tests"] = []
    return empty_dictionary


def add_image_in_multiple_test(dictionary_with_image_path_set, name="test", target_color=(0,0,0), top_left_x=0, top_left_y=0, bottom_right_x=-1, bottom_right_y=-1, tolerance=0, size_in_percentage=False, expected_percentage=0, show_region=False, percentage_range=0.5, bottom_right_delta=False):

    dictionary_with_image_path_set = eval(str(dictionary_with_image_path_set)); name = eval(str(name)); target_color = eval(str(target_color)); top_left_x = int(top_left_x); top_left_y = int(top_left_y); bottom_right_x = int(bottom_right_x); bottom_right_y = int(bottom_right_y); tolerance = eval(str(tolerance)); size_in_percentage = eval(str(size_in_percentage)); expected_percentage = eval(str(expected_percentage)); show_region = eval(str(show_region)); percentage_range = eval(str(percentage_range)); bottom_right_delta = eval(str(bottom_right_delta))

    if not bottom_right_delta:
        dict = {
            "name": name,
            "target_color": target_color,
            "top_left_x": top_left_x,
            "top_left_y": top_left_y,
            "bottom_right_x": bottom_right_x,
            "bottom_right_y": bottom_right_y,
            "tolerance": tolerance,
            "size_in_percentage": size_in_percentage,
            "expected_percentage": expected_percentage,
            "show_region": show_region,
            "percentage_range": percentage_range
        }
    else:
        dict = {
            "name": name,
            "target_color": target_color,
            "top_left_x": top_left_x,
            "top_left_y": top_left_y,
            "bottom_right_x": bottom_right_x + top_left_x,
            "bottom_right_y": bottom_right_y + top_left_y,
            "tolerance": tolerance,
            "size_in_percentage": size_in_percentage,
            "expected_percentage": expected_percentage,
            "show_region": show_region,
            "percentage_range": percentage_range
        }

    dictionary_with_image_path_set["tests"].append(dict)

    return dictionary_with_image_path_set


def run_multiple_tests(dictionary_with_path_and_tests, show_region=True):
    mult = MultipleAnalysis(dictionary_with_path_and_tests)
    results = mult.run_multiple_tests(show_region=show_region)
    return str(results)
