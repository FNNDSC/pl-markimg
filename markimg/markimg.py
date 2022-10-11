#
# markimg ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import matplotlib.pyplot as plt
import numpy as np
import json
import math
import os
import glob
import cv2


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

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-markimg markimg                           \
                /incoming /outgoing

    DESCRIPTION

        `markimg` ...

    ARGS

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
    PACKAGE                 = __package__
    TITLE                   = 'An app to mark landmark points and lines on an input image'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 2000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 8000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

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
        
        
        self.add_argument(  '--inputJsonName','-j',
                            dest         = 'inputJsonName',
                            type         = str,
                            optional     = True,
                            help         = 'Input file filter',
                            default      = 'prediction.json')
                            
        self.add_argument(  '--inputImageName','-i',
                            dest         = 'inputImageName',
                            type         = str,
                            optional     = True,
                            help         = 'Name of the png file',
                            default      = 'leg.png')
                            
        self.add_argument(  '--pointMarker','-p',
                            dest         = 'pointMarker',
                            type         = str,
                            optional     = True,
                            help         = 'Point marker',
                            default      = 'x')
                            
        self.add_argument(  '--pointColor','-c',
                            dest         = 'pointColor',
                            type         = str,
                            optional     = True,
                            help         = 'Color of point marker',
                            default      = 'red')
                            
        self.add_argument(  '--lineColor','-l',
                            dest         = 'lineColor',
                            type         = str,
                            optional     = True,
                            help         = 'Color of the line to be drawn',
                            default      = 'red')
                            
        self.add_argument(  '--textColor','-t',
                            dest         = 'textColor',
                            type         = str,
                            optional     = True,
                            help         = 'Color of text',
                            default      = 'white')
                            
        self.add_argument(  '--textHeight','-s',
                            dest         = 'textHeight',
                            type         = int,
                            optional     = True,
                            help         = 'Spatial distance of the text wrt x-axis of a line',
                            default      = 10)

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        # Output the space of CLI
        d_options = vars(options)
        for k,v in d_options.items():
            print("%20s: %-40s" % (k, v))
        print("")
        
        # Read json file first
        str_glob = '%s/**/%s' % (options.inputdir,options.inputJsonName)

        l_datapath = glob.glob(str_glob, recursive=True)
        
        jsonFilePath =l_datapath[0]
        
        print(f"Reading JSON file from {jsonFilePath}")
        
        f = open(jsonFilePath, 'r')
        data = json.load(f)
        
        d_landmarks = {}
        d_lines = {}
        for row in data:
            # Read image according to "key"
            image_path = os.path.join(row,options.inputImageName)
            
            file_path = ""
            for root, dirs, files in os.walk(options.inputdir):
                for dir in dirs:
                    if dir == row:
                        file_path = os.path.join(root,image_path)

            print(f"Reading input image from {file_path}")
            image = cv2.imread(file_path)
            
            resized_image = cv2.resize(image,(1024,512),interpolation = cv2.INTER_AREA)
            
               
            items = data[row]["landmarks"]
            for item in items:
                for i in item:
                    point = [item[i]["x"],item[i]["y"]]
                    d_landmarks[i] = point            
                    # Plot points
                    self.drawPoint(point,options.pointMarker,options.pointColor)   
                     
            items = data[row]["drawLine"]
            for item in items:
                for i in item:
                    start = d_landmarks[item[i]["start"]]
                    end = d_landmarks[item[i]["end"]]
                    d_lines[i] = [start,end]            
                    # Draw lines
                    self.drawLine(start,end,options.lineColor) 
                       
            items = data[row]["measureLine"]
            for item in items:        
                # Measure distance
                self.measureLine(d_lines[item],options.textColor,options.textHeight)
                
            plt.imshow(resized_image)      
            plt.savefig(os.path.join(options.outputdir,row+".png"))
            plt.clf()

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
        
    def drawPoint(self,point,marker,color):
        plt.scatter(point[0],point[1],marker=marker,color=color,s=100)
        
    def drawLine(self,start,end,color):
        X = []
        Y = []    
        X.append(start[0])
        X.append(end[0])
        Y.append(start[1])
        Y.append(end[1])    # draw connecting lines
        plt.plot(X,Y, color= color,linewidth=1)
        
    def measureLine(self,line,color,height):
        P1 = line[0]
        P2 = line[1]    
        distance = round(math.dist(P1,P2),0)    
        x = (P1[0]+P2[0])/2
        y = P1[1] - height    
        plt.text(x,y,distance, color=color)
        
         
