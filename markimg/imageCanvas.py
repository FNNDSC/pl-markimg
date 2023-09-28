"""
This class represents a canvas or X-Y plane of a certain height and width.
An object of this class offers the ability to move a point (x,y) on the canvas by using
simple direction commands (go_left, go_right, etc.). In addition to this, we can specify any
offset value to the current position
"""


class ImageCanvas:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.current_X = 0
        self.current_Y = 0

    def __get_left(self) -> (int, int):
        """
        A method to return the mid-point on the left border of
        the canvas
        :return: x-y coordinates
        """
        return 0, self.height / 2

    def __get_right(self) -> (int, int):
        """
        A method to return the mid-point of the right
        border of the canvas
        :return: x-y coordinates
        """
        return self.width, self.height / 2

    def __get_top(self) -> (int, int):
        """
        A method to return the mid-point of the top
        border of the canvas
        :return: x-y coordinates
        """
        return self.width / 2, self.height

    def __get_bottom(self) -> (int, int):
        """
        A method to return the mid-point of the bottom
        border of the canvas
        :return: x-y coordinates
        """
        return self.width / 2, 0

    def __get_center(self) -> (int, int):
        """
        A method to return the center of the X-Y plane
        :return: x-y coordinates
        """
        return self.width / 2, self.height / 2

    def go_left(self) -> (int, int):
        self.current_X, self.current_Y = self.__get_left()
        return self.current_X, self.current_Y

    def go_right(self) -> (int, int):
        self.current_X, self.current_Y = self.__get_right()
        return self.current_X, self.current_Y

    def go_top(self) -> (int, int):
        self.current_X, self.current_Y = self.__get_top()
        return self.current_X, self.current_Y

    def go_bottom(self) -> (int, int):
        self.current_X, self.current_Y = self.__get_bottom()
        return self.current_X, self.current_Y

    def go_center(self) -> (int, int):
        self.current_X, self.current_Y = self.__get_center()
        return self.current_X, self.current_Y

    def add_offset(self, offset_x: int, offset_y: int) -> (int, int):
        self.current_X += offset_x
        self.current_Y += offset_y
        return self.current_X, self.current_Y
