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
            [-j|--inputJsonName <jsonFileName>]                         \\
            [-i|--inputImageName <pngFileName>]                         \\
            [-p|--pointMarker <pointMarker>]                            \\
            [-c|--pointColor <pointColor>]                              \\
            [-l|--lineColor <lineColor>]                                \\
            [-t|--textColor <textColor>]                                \\
            [-s|--textSize <textSize>]                                  \\
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
        [-j|--inputJsonName <jsonFileName>] 
        The name of the input JSON file. Default is 'prection.json'
        
        [-i|--inputImageName <pngFileName>] 
        The name of the input png file. Default is 'leg.png' 
        
        [-p|--pointMarker <pointMarker>]
        A character that represents a point on the image. Default
        is 'x'
         
        [-c|--pointColor <pointColor>] 
        The color of the character representing points on the image.
        Default is red
        
        [-l|--lineColor <lineColor>]
        The color of the line drawn on the input image.
        Default is red 
        
        [-t|--textColor <textColor>]
        The color of the text placed on the input image.
        Default is white
        
        [-s|--textSize <textSize>]
        The size of the text on the input image.
        Default is "xx-small"         

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
                            help         = 'Input JSON file name',
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
                            
        self.add_argument(  '--textSize','-s',
                            dest         = 'textSize',
                            type         = str,
                            optional     = True,
                            help         = 'Size of the text displayed on image',
                            default      = 'xx-small')
                            
        self.add_argument(  '--linewidth','-w',
                            dest         = 'linewidth',
                            type         = float,
                            optional     = True,
                            help         = 'Width of lines on image',
                            default      = 1 )

        self.add_argument(  '--textPos','-q',
                            dest         = 'textPos',
                            type         = str,
                            optional     = True,
                            help         = 'Quadrant for displaying text on image',
                            default      = "bottom-right" )
                            
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
        d_lengths = {}
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
            plt.style.use('dark_background')
            plt.axis('off')
            
            max_y, max_x, max_z = image.shape
            height = data[row]["origHeight"]
            ht_scale = height/max_x
            
               
            items = data[row]["landmarks"]
            for item in items:
                for i in item:
                    point = [item[i]["x"],item[i]["y"]]
                    d_landmarks[i] = point            
                    # Plot points
                    self.drawPoint(point,options.pointMarker,options.pointColor)   
                     
            items = data[row]["drawXLine"]
            for item in items:
                for i in item:
                    start = d_landmarks[item[i]["start"]]
                    end = d_landmarks[item[i]["end"]]
                    d_lines[i] = [start,end]            
                    # Draw lines
                    self.drawXLine(start,end,options.lineColor, max_y,options.linewidth) 
                       
            items = data[row]["measureXDist"]
            for item in items:        
                # Measure distance
                length = self.measureXDist(d_lines[item],options.textColor,options.textSize,max_y,ht_scale)
                d_lengths[item] = length
                
            
            if (options.textPos == "bottom-right"):
                x_pos = max_x
                y_pos = 0
            elif (options.textPos == "bottom-left"):
                x_pos = max_x
                y_pos = max_y
            elif (options.textPos == "top-right"):
                x_pos = 0
                y_pos = 0
            elif (options.textPos == "top-left"):
                x_pos = 0
                y_pos = max_y
            
            x_pos = x_pos -210
            
            x1 = x_pos
            y1 = y_pos
                        
            
            leftLeg = self.printSum(x1,y1,d_lengths["leftTopLeg"],d_lengths["leftBottomLeg"],options.textColor,"cm","Left Leg Length",options.textSize)
            
            x2 = x_pos + 70
            y2 = y_pos 
            
            rightLeg = self.printSum(x2,y2,d_lengths["rightTopLeg"],d_lengths["rightBottomLeg"],options.textColor,"cm","Right Leg Length",options.textSize)
            
            x3 = x_pos + 140
            y3 = y_pos           
            self.printDiff(x3,y3,leftLeg,rightLeg,options.textColor,"cm","Leg Length Diff",options.textSize)
            plt.tick_params(left = False, right = False , labelleft = False ,
                labelbottom = False, bottom = False)
            plt.imshow(image)      
            plt.savefig(os.path.join("/tmp",row+".png"),dpi=250,bbox_inches = 'tight',pad_inches=0.0)
            plt.clf()
            png = cv2.imread(os.path.join("/tmp",row+".png"))
            inverted_png = cv2.rotate(png,cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite(os.path.join(options.outputdir,row+".png"),inverted_png)

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
        
    def drawPoint(self,point,marker,color):
        plt.scatter(point[0],point[1],marker=marker,color=color,s=100)
        
    def drawLine(self,start,end,color,linewidth):
        X = []
        Y = []    
        X.append(start[0])
        X.append(end[0])
        Y.append(start[1])
        Y.append(end[1])    
        # draw connecting lines
        plt.plot(X,Y, color= color,linewidth=linewidth)
        
    def measureLine(self,line,color,size,unit='px'):
        P1 = line[0]
        P2 = line[1]    
        distance = round(math.dist(P1,P2))
        display_text = str(distance) + unit 
        x = (P1[0]+P2[0])/2
        y = P1[1] - 10    
        plt.text(x,y,display_text, color=color,fontsize=size)
        return distance
        
    def printDiff(self,x,y,val1,val2,color,unit,title,size,scaleFactor=1):
        diff = round(abs(val1 - val2),1)
        display_text = title + "=" + str(diff) + unit
        plt.text(x,y,display_text,color=color,fontsize=size,rotation=90)
        return diff
        
    def printSum(self,x,y,val1,val2,color,unit,title,size,scaleFactor=1):
        sum = round((val1 + val2),1)
        display_text = title + "=" + str(sum) + unit
        plt.text(x,y,display_text,color=color,fontsize=size,rotation=90)
        return sum
        
    def measureXDist(self,line,color,size,max_y,scale, unit='cm'):
        P1 = line[0]
        P2 = line[1]    
        distance = round((abs(P1[0]-P2[0]) * scale)/10,1)
        display_text = str(distance) + unit    
        x = (P1[0]+P2[0])/2    
        if((max_y - P1[1])<(P2[1]-0)):
            y = max_y-100
        else:
            y = -100   
        plt.text(x,y,display_text , color=color,size=size, rotation=90)
        return distance
        
    def drawXLine(self,start,end,color, max_y,linewidth):
        X = []
        Y = []            
        X.append(start[0])
        X.append(end[0])
        if((max_y - start[1])<(start[1]-0)):
            Y.append(max_y-10)
            Y.append(max_y-10)
        else:
            Y.append(10)
            Y.append(10)          
        # draw connecting lines
        plt.plot(X,Y, color= color,linewidth=linewidth)
        P1 = start
        P2 = [start[0],Y[0]]
        
        self.drawLine(start,[start[0],Y[0]],color,linewidth)
        self.drawLine(end,[end[0],Y[1]],color,linewidth)
         
