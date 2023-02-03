pl-markimg
================================

.. image:: https://img.shields.io/docker/v/fnndsc/pl-markimg?sort=semver
    :target: https://hub.docker.com/r/fnndsc/pl-markimg

.. image:: https://img.shields.io/github/license/fnndsc/pl-markimg
    :target: https://github.com/FNNDSC/pl-markimg/blob/master/LICENSE

.. image:: https://github.com/FNNDSC/pl-markimg/workflows/ci/badge.svg
    :target: https://github.com/FNNDSC/pl-markimg/actions


.. contents:: Table of Contents


Abstract
--------

An app to mark landmark points and lines on an input image


Description
-----------


``markimg`` is a *ChRIS ds-type* application that consumes upstream information about landmarks in an image, and generates measurement lines on the actual image itself. Additionally, it also generates a mini-report, embedded within the image itself as well a text (JSON) file.

Usage
-----

.. code::

    docker run --rm fnndsc/pl-markimg markimg
        [-j|--inputJsonName <jsonFileName>]
        [-i|--inputImageName <pngFileName>]
        [-p|--pointMarker <pointMarker>]
        [-c|--pointColor <pointColor>]
        [-l|--lineColor <lineColor>]
        [-t|--textColor <textColor>]
        [-s|--textSize <textSize>]
        [-w|--lineWidth <lineWidth>]
        [-q|--textPos <textPosition>]
        [-g|--lineGap <lineGap>]
        [-z|--pointSize <sizeInPixels>]
        [-h|--help]
        [--json] [--man] [--meta]
        [--savejson <DIR>]
        [-v|--verbosity <level>]
        [--version]
        <inputDir> <outputDir>


Arguments
~~~~~~~~~

.. code::

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


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-markimg markimg --man

Run
~~~

You need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-markimg markimg                           \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-markimg .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-markimg nosetests

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
