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

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        
        # Read json file firstf = open('/home/sandip/prediction.json', 'r')
        d_landmarks = {}
        d_lines = {}
        for row in data:
            # Read image according to "key"
            image = cv2.imread('/home/sandip/dcm-out/'+row+"/leg.png") 
               
            items = data[row]["landmarks"]
            for item in items:
                for i in item:
                    point = [item[i]["x"],item[i]["y"]]
                    d_landmarks[i] = point            
                    # Plot points
                    drawPoint(point,POINT_MARKER,POINT_COLOR)   
                     
            items = data[row]["drawLine"]
            for item in items:
                for i in item:
                    start = d_landmarks[item[i]["start"]]
                    end = d_landmarks[item[i]["end"]]
                    d_lines[i] = [start,end]            
                    # Draw lines
                    drawLine(start,end,LINE_COLOR) 
                       
            items = data[row]["measureLine"]
            for item in items:        
                # Measure distance
                measureLine(d_lines[item],TEXT_COLOR,TEXT_HEIGHT)
                
                   
            plt.imshow(image)
            plt.show()

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
        
         
