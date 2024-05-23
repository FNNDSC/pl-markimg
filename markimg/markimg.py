#
# markimg ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import glob
import json
import math
import os
import sys

import cv2
import matplotlib.pyplot as plt
from chrisapp.base import ChrisApp
from loguru import logger
from pflog import pflog
from markimg.imageCanvas import ImageCanvas

LOG = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors=True)
logger.add(sys.stderr, format=logger_format)

Gstr_title = r"""
                      _    _
                     | |  (_)
 _ __ ___   __ _ _ __| | ___ _ __ ___   __ _
| '_ ` _ \ / _` | '__| |/ / | '_ ` _ \ / _` |
| | | | | | (_| | |  |   <| | | | | | | (_| |
|_| |_| |_|\__,_|_|  |_|\_\_|_| |_| |_|\__, |
                                        __/ |
                                       |___/
"""

Gstr_synopsis = """

    NAME

       markimg

    SYNOPSIS

        docker run --rm fnndsc/pl-markimg markimg                       \\
            [-j|--inputJsonName <jsonFileName>]                         \\
            [-i|--inputImageName <pngFileName>]                         \\
            [-p|--pointMarker <pointMarker>]                            \\
            [-c|--pointColor <pointColor>]                              \\
            [-l|--lineColor <lineColor>]                                \\
            [-t|--textColor <textColor>]                                \\
            [-s|--textSize <textSize>]                                  \\
            [-w|--lineWidth <lineWidth>]                                \\
            [-q|--textPos <textPosition>]                               \\
            [-g|--lineGap <lineGap>]                                    \\
            [-z|--pointSize <sizeInPixels>]                             \\
            [--pftelDB <DBURLpath>]                                     \\
            [--addText <additionalText>]                                \\
            [--addTextSize <additionalTextSize>]                        \\
            [--addTextPos <additionalTextPosition>]                     \\
            [--addTextColor <additionalTextColor>]                      \\
            [--addTextOffset <additionalTextOffsetPosition>]            \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                                 \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing          \\
                fnndsc/pl-markimg markimg                               \\
                /incoming /outgoing

    DESCRIPTION

        `markimg` is a ChRIS DS plugin that is responsible for adding
        measurement markers to an image file and generating a mini
        text (JSON) report.

    ARGS

        [-j|--inputJsonName <jsonFileName>]
        The name of the input JSON file.
        Default is 'prediction.json'.

        [-i|--inputImageName <pngFileName>]
        The name of the input image file.
        Default is 'leg.png'.

        [-p|--pointMarker <pointMarker>]
        A character that represents a point on the image.
        Default is 'x'.

        [-c|--pointColor <pointColor>]
        The color of the character representing points on the image.
        Default is 'red'.

        [-l|--lineColor <lineColor>]
        The color of the line drawn on the input image.
        Default is 'red'.

        [-t|--textColor <textColor>]
        The color of the text placed on the input image.
        Default is 'white'.

        [-s|--textSize <textSize>]
        The size of the text on the input image.
        Default is '5'.

        [-w|--lineWidth <lineWidth>]
        The width of line to be drawn on an input image.
        Default is '1'.

        [-q|--textPos <textPosition>]
        The position of text on an image.
        Default is 'right'.

        [-g|--lineGap <lineGap>]
        Space between lines in pixels.
        Default is '20'.

        [-z|--pointSize <sizeInPixels>]
        The size of points to be plotted on the image.
        Default is '10'.

        [--pftelDB <DBURLpath>]
        If specified, send telemetry logging to the pftel server and the
        specfied DBpath:

            --pftelDB   <URLpath>/<logObject>/<logCollection>/<logEvent>

        for example

            --pftelDB http://localhost:22223/api/v1/weather/massachusetts/boston

        Indirect parsing of each of the object, collection, event strings is
        available through `pftag` so any embedded pftag SGML is supported. So

            http://localhost:22223/api/vi/%platform/%timestamp_strmsk|**********_/%name

        would be parsed to, for example:

            http://localhost:22223/api/vi/Linux/2023-03-11/posix
            
        [--addText <additionalText>]  
        If specified, burn this additional text on the final image.   
                                   
        [--addTextSize <additionalTextSize>]   
        The size of the additional text to be shown on the image.
        Default is 5.  
                           
        [--addTextPos <additionalTextPosition>]   
        The position of the additional text to be shown on the image.  
        Default is right. 
                       
        [--addTextColor <additionalTextColor>] 
        The color of the additional text to be shown on the image. 
        Default is white.
        
        [--addTextOffset <additionalTextOffset>]
        If specified, move the additional text using the offset 
        coordinates (x,y). Accepts a tuple in the form of "x,y"
        
                       
        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.
"""


class Markimg(ChrisApp):
    """
    An app to mark landmark points and lines on an input image
    """
    PACKAGE = __package__
    TITLE = 'An app to mark landmark points and lines on an input image'
    CATEGORY = ''
    TYPE = 'ds'
    ICON = ''  # url of an icon image
    MIN_NUMBER_OF_WORKERS = 1  # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS = 1  # Override with the maximum number of workers as int
    MIN_CPU_LIMIT = 2000  # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT = 8000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT = 0  # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT = 0  # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

        self.add_argument('--inputJsonName', '-j',
                          dest='inputJsonName',
                          type=str,
                          optional=True,
                          help='Input JSON file name',
                          default='prediction.json')

        self.add_argument('--inputImageName', '-i',
                          dest='inputImageName',
                          type=str,
                          optional=True,
                          help='Name of the input image file',
                          default='leg.png')

        self.add_argument('--pointMarker', '-p',
                          dest='pointMarker',
                          type=str,
                          optional=True,
                          help='Point marker',
                          default='x')

        self.add_argument('--pointColor', '-c',
                          dest='pointColor',
                          type=str,
                          optional=True,
                          help='Color of point marker',
                          default='red')

        self.add_argument('--lineColor', '-l',
                          dest='lineColor',
                          type=str,
                          optional=True,
                          help='Color of the line to be drawn',
                          default='red')

        self.add_argument('--textColor', '-t',
                          dest='textColor',
                          type=str,
                          optional=True,
                          help='Color of text',
                          default='white')

        self.add_argument('--textSize', '-s',
                          dest='textSize',
                          type=float,
                          optional=True,
                          help='Size of the text displayed on image',
                          default=5)

        self.add_argument('--linewidth', '-w',
                          dest='linewidth',
                          type=float,
                          optional=True,
                          help='Width of lines on image',
                          default=1)

        self.add_argument('--textPos', '-q',
                          dest='textPos',
                          type=str,
                          optional=True,
                          help='Position of text placement on an input image; left or right',
                          default="right")

        self.add_argument('--lineGap', '-g',
                          dest='lineGap',
                          type=int,
                          optional=True,
                          help='Space between lines in pixels',
                          default=20)

        self.add_argument('--pointSize', '-z',
                          dest='pointSize',
                          type=int,
                          optional=True,
                          help='The size of points to be plotted on the image',
                          default=10)
        self.add_argument('--pftelDB',
                          dest='pftelDB',
                          default='',
                          type=str,
                          optional=True,
                          help='optional pftel server DB path')
        self.add_argument('--addText',
                          dest='addText',
                          default='',
                          type=str,
                          optional=True,
                          help='optional text to add on the final image')
        self.add_argument('--addTextPos',
                          dest='addTextPos',
                          default='right',
                          type=str,
                          optional=True,
                          help='Position of additional text on the final output,'
                               'the available choices are top, bottom, left, right and across')
        self.add_argument('--addTextSize',
                          dest='addTextSize',
                          default=5,
                          type=float,
                          optional=True,
                          help='Size of additional text on the final output,'
                               'default value is 5')
        self.add_argument('--addTextColor',
                          dest='addTextColor',
                          default='white',
                          type=str,
                          optional=True,
                          help='Color of additional text on the final output,'
                               'default value is white')
        self.add_argument('--addTextOffset',
                          dest='addTextOffset',
                          default='0,0',
                          type=str,
                          optional=True,
                          help='Offset of additional text on the final output,'
                               'default value is 0,0')

    def preamble_show(self, options) -> None:
        """
        Just show some preamble "noise" in the output terminal
        """

        LOG(Gstr_title)
        LOG('Version: %s' % self.get_version())

        LOG("plugin arguments...")
        for k, v in options.__dict__.items():
            LOG("%25s:  [%s]" % (k, v))
        LOG("")

        LOG("base environment...")
        for k, v in os.environ.items():
            LOG("%25s:  [%s]" % (k, v))
        LOG("")

    @pflog.tel_logTime(
        event='markimg',
        log='Draw line segments between landmark points on an input image'
    )
    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        self.preamble_show(options)

        # Read json file first
        str_glob = '%s/**/%s' % (options.inputdir, options.inputJsonName)

        l_datapath = glob.glob(str_glob, recursive=True)

        jsonFilePath = l_datapath[0]

        LOG(f"Reading JSON file from {jsonFilePath}")

        f = open(jsonFilePath, 'r')
        data = json.load(f)

        d_landmarks = {}
        d_lines = {}
        d_lengths = {}
        d_json = {}
        row = ""
        for row in data:

            file_path = []
            for root, dirs, files in os.walk(options.inputdir):
                for dir in dirs:
                    if dir == row:
                        dir_path = os.path.join(root, dir)
                        file_path = glob.glob(dir_path + '/**/' + options.inputImageName, recursive=True)

            LOG(f"Reading input image from {file_path[0]}")
            image = cv2.imread(file_path[0])
            plt.style.use('dark_background')
            plt.axis('off')

            max_y, max_x, max_z = image.shape
            img_XY_plane: ImageCanvas = ImageCanvas(max_y, max_x)
            height = data[row]["origHeight"]
            ht_scale = height / max_x

            info = data[row]['info']
            details = data[row]['details']

            items = data[row]["landmarks"]
            for item in items:
                for i in item:
                    point = [item[i]["x"], item[i]["y"]]
                    d_landmarks[i] = point
                    # Plot points
                    self.drawPoint(point, options.pointMarker, options.pointColor, options.pointSize)

            items = data[row]["drawXLine"]
            for item in items:
                for i in item:
                    start = d_landmarks[item[i]["start"]]
                    end = d_landmarks[item[i]["end"]]
                    d_lines[i] = [start, end]
                    # Draw lines
                    self.drawXLine(start, end, options.lineColor, max_y, options.linewidth, i)

            items = data[row]["measureXDist"]
            d_pixel = {}
            for item in items:
                # Measure distance
                px_length, length = self.measureXDist(d_lines[item], options.textColor, options.textSize, max_y,
                                                      ht_scale)
                d_lengths[item] = length
                d_pixel[item] = px_length

            unit = 'cm'
            warning_msg = ''
            if ht_scale == 0:
                unit = 'px'
                warning_msg = ('WARNING: \n'
                               'DICOM is missing FOVDimension tag.\n'
                               'Calculations in cm are not possible.')

            if options.textPos == "left":
                x_pos = 0
                y_pos = max_y
            elif options.textPos == "right":
                x_pos = 0
                y_pos = 0

            line_gap = options.lineGap

            y_pos = y_pos - line_gap

            d_info = {}
            # Print image info
            for field in info.keys():
                x_pos = x_pos + line_gap
                display_text = field + ": " + str(info[field])
                d_info[field] = info[field]
                plt.text(x_pos, y_pos, display_text, color='white', fontsize=options.textSize, rotation=90)

            # Print some blank lines
            for i in range(0, 3):
                x_pos = x_pos + line_gap
                plt.text(x_pos, y_pos, '', color='white', fontsize=options.textSize, rotation=90)

            d_femur = {}
            # Print specific details about the image
            rightFemurInfo = 'Right femur: ' + str(d_lengths['Right femur']) + f' {unit}'
            d_femur['Right femur'] = str(d_lengths['Right femur']) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, rightFemurInfo, color='white', fontsize=options.textSize, rotation=90)

            leftFemurInfo = 'Left femur: ' + str(d_lengths['Left femur']) + f' {unit}'
            d_femur['Left femur'] = str(d_lengths['Left femur']) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, leftFemurInfo, color='white', fontsize=options.textSize, rotation=90)

            femurDiffInfo = str(self.getDiff(d_lengths['Right femur'], d_lengths['Left femur'])) + f' {unit}, ' + \
                            self.compareLength(d_lengths['Left femur'], d_lengths['Right femur'])

            femurDiffText = 'Difference: ' + femurDiffInfo
            d_femur['Difference'] = femurDiffInfo
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, femurDiffText, color='white', fontsize=options.textSize, rotation=90)

            # blank line
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, '', color='white', fontsize=options.textSize, rotation=90)

            d_tibia = {}
            rightTibiaInfo = 'Right tibia: ' + str(d_lengths['Right tibia']) + f' {unit}'
            d_tibia['Right tibia'] = str(d_lengths['Right tibia']) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, rightTibiaInfo, color='white', fontsize=options.textSize, rotation=90)

            leftTibiaInfo = 'Left tibia: ' + str(d_lengths['Left tibia']) + f' {unit}'
            d_tibia['Left tibia'] = str(d_lengths['Left tibia']) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, leftTibiaInfo, color='white', fontsize=options.textSize, rotation=90)

            tibiaDiffInfo = str(self.getDiff(d_lengths['Right tibia'], d_lengths['Left tibia'])) + f' {unit}, ' + \
                            self.compareLength(d_lengths['Left tibia'], d_lengths['Right tibia'])

            tibaiDiffText = 'Difference: ' + tibiaDiffInfo
            d_tibia['Difference'] = tibiaDiffInfo
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, tibaiDiffText, color='white', fontsize=options.textSize, rotation=90)

            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, '', color='white', fontsize=options.textSize, rotation=90)

            d_total = {}
            totalRightInfo = 'Total right: ' + str(
                self.getSum(d_lengths['Right femur'], d_lengths['Right tibia'])) + f' {unit}'
            d_total['Total right'] = str(self.getSum(d_lengths['Right femur'], d_lengths['Right tibia'])) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, totalRightInfo, color='white', fontsize=options.textSize, rotation=90)

            totalLeftInfo = 'Total left: ' + str(
                self.getSum(d_lengths['Left femur'], d_lengths['Left tibia'])) + f' {unit}'
            d_total['Total left'] = str(self.getSum(d_lengths['Left femur'], d_lengths['Left tibia'])) + f' {unit}'
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, totalLeftInfo, color='white', fontsize=options.textSize, rotation=90)

            totalDiff = self.getDiff(self.getSum(d_lengths['Left femur'], d_lengths['Left tibia']),
                                     self.getSum(d_lengths['Right femur'], d_lengths['Right tibia']))
            totalComp = self.compareLength(self.getSum(d_lengths['Left femur'], d_lengths['Left tibia']),
                                           self.getSum(d_lengths['Right femur'], d_lengths['Right tibia']))

            totalDiffInfo = str(totalDiff) + f' {unit}, ' + totalComp
            totalDiffText = 'Total difference: ' + totalDiffInfo
            d_total['Difference'] = totalDiffInfo
            x_pos = x_pos + line_gap
            plt.text(x_pos, y_pos, totalDiffText, color='white', fontsize=options.textSize, rotation=90)

            if warning_msg:
                # Print some blank lines
                for i in range(0, 2):
                    x_pos = x_pos + line_gap
                    plt.text(x_pos, y_pos, '', color='white', fontsize=options.textSize, rotation=90)
                rotation = 0
                plt.text(x_pos, y_pos, warning_msg, color='cyan', fontsize=options.textSize, rotation=90)
            for i in range(0, 4):
                x_pos = x_pos + line_gap
                plt.text(x_pos, y_pos, '', color='white', fontsize=options.textSize, rotation=90)
            plt.text(x_pos, y_pos, options.addText, color=options.addTextColor, fontsize=options.addTextSize,
                     rotation=90)

            """
            Need to rewrite logic for directions.
            """
            if options.addTextPos == "left":
                x_pos, y_pos = img_XY_plane.go_top()
            elif options.addTextPos == "right":
                x_pos, y_pos = img_XY_plane.go_bottom()
            elif options.addTextPos == "bottom":
                x_pos, y_pos = img_XY_plane.go_right()
                rotation = 90
            elif options.addTextPos == "top":
                x_pos, y_pos = img_XY_plane.go_left()
                rotation = 90
            elif options.addTextPos == "across":
                x_pos, y_pos = img_XY_plane.go_center()
                rotation = 90  # 135: diagonal [bottom-left - top-right]
            else:
                raise Exception(f"Incorrect line position specified: {options.linePos}")

            if len(options.addTextOffset):
                offset = options.addTextOffset.split(',')
                offset_y = int(offset[0])
                offset_x = int(offset[1])
                x_pos, y_pos = img_XY_plane.add_offset(-offset_x, -offset_y)

            # y_pos = y_pos - line_gap

            # plt.text(x_pos, y_pos, options.addText, color=options.addTextColor, fontsize=options.addTextSize,
            #         rotation=rotation)

            # Clean up all matplotlib stuff and save as PNG
            plt.tick_params(left=False, right=False, labelleft=False,
                            labelbottom=False, bottom=False)

            plt.imshow(image)
            plt.savefig(os.path.join("/tmp", row + "img.png"), bbox_inches='tight', pad_inches=0.0)
            tmppng = cv2.imread(os.path.join("/tmp", row + "img.png"))
            y, x, z = tmppng.shape
            dpi = (max_x / x) * 100
            LOG(f"Input image dimensions {image.shape}")
            LOG(f'Applying DPI {dpi} to the output image')

            plt.savefig(os.path.join("/tmp", row + ".png"), dpi=dpi, bbox_inches='tight', pad_inches=0.0)
            plt.clf()
            png = cv2.imread(os.path.join("/tmp", row + ".png"))
            inverted_png = cv2.rotate(png, cv2.ROTATE_90_CLOCKWISE)

            LOG(f"Output image dimensions {png.shape}")
            cv2.imwrite(os.path.join(options.outputdir, row + ".png"), inverted_png)
            d_json[row] = {'info': d_info, 'femur': d_femur, 'tibia': d_tibia, 'total': d_total,
                           'pixel_distance': d_pixel, 'details': details}

        jsonFilePath = os.path.join(options.outputdir, f'{row}-analysis.json')
        # Open a json writer, and use the json.dumps()
        # function to dump data
        LOG("Saving %s" % jsonFilePath)
        with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(d_json, indent=4))

    def show_man_page(self):
        """
        Print the app's man page.
        """
        LOG(Gstr_synopsis)

    def drawPoint(self, point, marker, color, size):
        plt.scatter(point[0], point[1], marker=marker, color=color, s=size)

    def drawLine(self, start, end, color, linewidth):
        X = []
        Y = []
        X.append(start[0])
        X.append(end[0])
        Y.append(start[1])
        Y.append(end[1])
        # draw connecting lines
        plt.plot(X, Y, color=color, linewidth=linewidth)

    def measureLine(self, line, color, size, unit='px'):
        P1 = line[0]
        P2 = line[1]
        distance = round(math.dist(P1, P2))
        display_text = str(distance) + unit
        x = (P1[0] + P2[0]) / 2
        y = P1[1] - 10
        plt.text(x, y, display_text, color=color, fontsize=size)
        return distance

    def getDiff(self, val1, val2):
        diff = round(abs(val1 - val2), 1)
        return diff

    def getSum(self, val1, val2):
        sum = round((val1 + val2), 1)
        return sum

    def compareLength(self, left, right):
        compareText = "equal"
        try:
            if left > right:
                compareText = f'left longer ({round(((left - right) / right) * 100, 1)}%)'
            elif right > left:
                compareText = f'right longer ({round(((right - left) / left) * 100, 1)}%)'
        except ZeroDivisionError:
            compareText = "Error: ZeroDivisionError"

        return compareText + '    '

    def measureXDist(self, line, color, size, max_y, scale, unit='cm'):
        P1 = line[0]
        P2 = line[1]
        pixel_distance = round(abs(P1[0] - P2[0]))
        actual_distance = round((pixel_distance * scale) / 10, 1)
        if scale == 0:
            return pixel_distance, pixel_distance
        return pixel_distance, actual_distance

    def drawXLine(self, start, end, color, max_y, linewidth, bone_name):
        X = []
        Y = []
        X.append(start[0])
        X.append(end[0])
        if "Right" in bone_name:
            Y.append(max_y - 10)
            Y.append(max_y - 10)
        else:
            Y.append(10)
            Y.append(10)
        # draw connecting lines
        plt.plot(X, Y, color=color, linewidth=linewidth)
        P1 = start
        P2 = [start[0], Y[0]]

        self.drawLine(start, [start[0], Y[0]], color, linewidth)
        self.drawLine(end, [end[0], Y[1]], color, linewidth)
