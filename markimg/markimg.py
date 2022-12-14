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
import matplotlib.legend as lgnd


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
        The name of the input image file. Default is 'leg.png' 
        
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
        Default is 5
        
        [-w|--lineWidth <lineWidth>]
        The width of line to be drawn on an input image.
        Default is 1
                                       
        [-q|--textPos <textPosition>]                                     
        The position of text on an image.
        Default is right
        
        [-g|--lineGap <lineGap>]
        Space between lines in pixels.
        Default is 20.
        
        [-z|--pointSize <sizeInPixels>]
        The size of points to be plotted on the image.
        Default is 10.
        
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
                            help         = 'Name of the input image file',
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
                            type         = float,
                            optional     = True,
                            help         = 'Size of the text displayed on image',
                            default      = 5)
                            
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
                            help         = 'Position of text placement on an input image; left or right',
                            default      = "right" )
                            
        self.add_argument(  '--lineGap','-g',
                            dest         = 'lineGap',
                            type         = int,
                            optional     = True,
                            help         = 'Space between lines in pixels',
                            default      = 20 )
                            
        self.add_argument(  '--pointSize','-z',
                            dest         = 'pointSize',
                            type         = int,
                            optional     = True,
                            help         = 'The size of points to be plotted on the image',
                            default      = 10 )
                            
                            
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
        d_json = {}
        jsonFilePath = os.path.join(options.outputdir,'analysis.json')
        for row in data:
            
            file_path = []
            for root, dirs, files in os.walk(options.inputdir):
                for dir in dirs:
                    if dir == row:
                        dir_path = os.path.join(root,dir)
                        file_path = glob.glob(dir_path+'/**/'+options.inputImageName,recursive=True)

            print(f"\nReading input image from {file_path[0]}")
            image = cv2.imread(file_path[0])
            plt.style.use('dark_background')
            plt.axis('off')
            
            max_y, max_x, max_z = image.shape
            height = data[row]["origHeight"]
            ht_scale = height/max_x
            
            info = data[row]['info']
            
               
            items = data[row]["landmarks"]
            for item in items:
                for i in item:
                    point = [item[i]["x"],item[i]["y"]]
                    d_landmarks[i] = point            
                    # Plot points
                    self.drawPoint(point,options.pointMarker,options.pointColor,options.pointSize)   
                     
            items = data[row]["drawXLine"]
            for item in items:
                for i in item:
                    start = d_landmarks[item[i]["start"]]
                    end = d_landmarks[item[i]["end"]]
                    d_lines[i] = [start,end]            
                    # Draw lines
                    self.drawXLine(start,end,options.lineColor, max_y,options.linewidth) 
                       
            items = data[row]["measureXDist"]
            d_pixel = {}
            for item in items:        
                # Measure distance
                px_length,length = self.measureXDist(d_lines[item],options.textColor,options.textSize,max_y,ht_scale)
                d_lengths[item] = length
                d_pixel[item] = px_length
            
            if (options.textPos == "left"):
                x_pos = 0
                y_pos = max_y
            elif (options.textPos == "right"):
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
                plt.text(x_pos,y_pos,display_text,color='white',fontsize=options.textSize,rotation=90)
                
            # Print some blank lines
            for i in range(0,3):
                x_pos = x_pos + line_gap
                plt.text(x_pos,y_pos,'',color='white',fontsize=options.textSize,rotation=90)
            
            
            d_femur = {}    
            # Print specific details about the image    
            rightFemurInfo = 'Right femur: ' + str(d_lengths['Right femur']) + ' cm'
            d_femur['Right femur'] = str(d_lengths['Right femur']) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,rightFemurInfo,color='white',fontsize=options.textSize,rotation=90)
            
            leftFemurInfo = 'Left femur: ' + str(d_lengths['Left femur']) + ' cm'
            d_femur['Left femur'] = str(d_lengths['Left femur']) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,leftFemurInfo,color='white',fontsize=options.textSize,rotation=90)
            
            femurDiffInfo = str(self.getDiff(d_lengths['Right femur'],d_lengths['Left femur'])) + ' cm, ' + \
            self.compareLength(d_lengths['Left femur'],d_lengths['Right femur'])
            
            femurDiffText ='Difference: ' + femurDiffInfo
            d_femur['Difference'] = femurDiffInfo 
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,femurDiffText,color='white',fontsize=options.textSize,rotation=90)
            
            # blank line
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,'',color='white',fontsize=options.textSize,rotation=90)

            d_tibia = {}
            rightTibiaInfo = 'Right tibia: ' + str(d_lengths['Right tibia']) + ' cm'
            d_tibia['Right tibia'] = str(d_lengths['Right tibia']) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,rightTibiaInfo,color='white',fontsize=options.textSize,rotation=90)
            
            leftTibiaInfo = 'Left tibia: ' + str(d_lengths['Left tibia']) + ' cm'
            d_tibia['Left tibia'] = str(d_lengths['Left tibia']) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,leftTibiaInfo,color='white',fontsize=options.textSize,rotation=90)
            
            tibiaDiffInfo = str(self.getDiff(d_lengths['Right tibia'],d_lengths['Left tibia'])) + ' cm, ' + \
            self.compareLength(d_lengths['Left tibia'],d_lengths['Right tibia'])
            
            tibaiDiffText = 'Difference: ' + tibiaDiffInfo
            d_tibia['Difference'] = tibiaDiffInfo
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,tibaiDiffText,color='white',fontsize=options.textSize,rotation=90)
            
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,'',color='white',fontsize=options.textSize,rotation=90)

            
            d_total = {}
            totalRightInfo = 'Total right: ' + str(self.getSum(d_lengths['Right femur'],d_lengths['Right tibia'])) + ' cm'
            d_total['Total right'] = str(self.getSum(d_lengths['Right femur'],d_lengths['Right tibia'])) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,totalRightInfo,color='white',fontsize=options.textSize,rotation=90)
            
            totalLeftInfo = 'Total left: ' + str(self.getSum(d_lengths['Left femur'],d_lengths['Left tibia'])) + ' cm'
            d_total['Total left'] = str(self.getSum(d_lengths['Left femur'],d_lengths['Left tibia'])) + ' cm'
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,totalLeftInfo,color='white',fontsize=options.textSize,rotation=90)
            
            totalDiff = self.getDiff(self.getSum(d_lengths['Left femur'],d_lengths['Left tibia']), \
            self.getSum(d_lengths['Right femur'],d_lengths['Right tibia']))
            totalComp = self.compareLength(self.getSum(d_lengths['Left femur'],d_lengths['Left tibia']), \
            self.getSum(d_lengths['Right femur'],d_lengths['Right tibia']))
            
            totalDiffInfo = str(totalDiff) + ' cm, '+ totalComp
            totalDiffText = 'Total difference: ' + totalDiffInfo
            d_total['Difference'] = totalDiffInfo
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,totalDiffText,color='white',fontsize=options.textSize,rotation=90)
            
            x_pos = x_pos + line_gap
            plt.text(x_pos,y_pos,'',color='white',fontsize=options.textSize,rotation=90)
          
                        
            # Clean up all matplotlib stuff and save as PNG
            plt.tick_params(left = False, right = False , labelleft = False ,
                labelbottom = False, bottom = False)
                
            plt.imshow(image)  
            plt.savefig(os.path.join("/tmp",row+"img.png"),bbox_inches = 'tight',pad_inches=0.0)    
            tmppng = cv2.imread(os.path.join("/tmp",row+"img.png"))
            y,x,z = tmppng.shape
            dpi = (max_x/x) * 100
            print("\nInput image dimensions",image.shape)
            print(f'\nApplying DPI {dpi} to the output image')
            
            plt.savefig(os.path.join("/tmp",row+".png"),dpi = dpi,bbox_inches = 'tight',pad_inches=0.0)
            plt.clf()
            png = cv2.imread(os.path.join("/tmp",row+".png"))            
            inverted_png = cv2.rotate(png,cv2.ROTATE_90_CLOCKWISE)
            

            print("\nOutput image dimensions",png.shape)
            cv2.imwrite(os.path.join(options.outputdir,row+".png"),inverted_png)
            d_json[row] = {'info':d_info,'femur':d_femur,'tibia':d_tibia,'total':d_total,'pixel_distance':d_pixel}
            
        # Open a json writer, and use the json.dumps()
        # function to dump data
        with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(d_json, indent=4))

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
        
    def drawPoint(self,point,marker,color,size):
        plt.scatter(point[0],point[1],marker=marker,color=color,s=size)
        
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
        
    def getDiff(self,val1,val2):
        diff = round(abs(val1 - val2),1)
        return diff
        
    def getSum(self,val1,val2):
        sum = round((val1 + val2),1)
        return sum
    
    def compareLength(self,left,right):
        compareText = "equal"
        if left > right:
            compareText = 'left longer'
        elif right > left:
            compareText = 'right longer'
            
        return compareText + '    '
        
        
    def measureXDist(self,line,color,size,max_y,scale, unit='cm'):
        P1 = line[0]
        P2 = line[1]
        pixel_distance = round(abs(P1[0]-P2[0]))
        actual_distance = round((pixel_distance * scale)/10,1)
        return pixel_distance, actual_distance
        
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
         
