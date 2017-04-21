from PyQt5.QtWidgets import QWidget, QFrame, QScrollArea, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation


class GroupWidget(QWidget):
    def __init__(self, parent=None, title='', animation_duration=300):
        """
        References:
            # Adapted from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(GroupWidget, self).__init__(parent=parent)

        self.animation_duration = animation_duration
        self.toggle_animation = QParallelAnimationGroup()
        self.content_area = QScrollArea()
        self.header_line = QFrame()
        self.toggle_button = QToolButton()
        self.main_layout = QGridLayout()

        toggle_button = self.toggle_button
        toggle_button.setStyleSheet("QToolButton { border: none; }")
        toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toggle_button.setArrowType(Qt.RightArrow)
        toggle_button.setText(str(title))
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)

        header_line = self.header_line
        header_line.setFrameShape(QFrame.HLine)
        header_line.setFrameShadow(QFrame.Sunken)
        header_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.content_area.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # start out collapsed
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggle_animation = self.toggle_animation
        toggle_animation.addAnimation(QPropertyAnimation(self, bytes("minimumHeight", "utf-8")))
        toggle_animation.addAnimation(QPropertyAnimation(self, bytes("maximumHeight", "utf-8")))
        toggle_animation.addAnimation(QPropertyAnimation(self.content_area, bytes("maximumHeight", "utf-8")))
        # don't waste space
        main_layout = self.main_layout
        main_layout.setVerticalSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        row = 0
        main_layout.addWidget(self.toggle_button, row, 0, 1, 1, Qt.AlignLeft)
        main_layout.addWidget(self.header_line, row, 2, 1, 1)
        row += 1
        main_layout.addWidget(self.content_area, row, 0, 1, 3)
        self.setLayout(self.main_layout)

        def start_animation(checked):
            arrow_type = Qt.DownArrow if checked else Qt.RightArrow
            direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
            toggle_button.setArrowType(arrow_type)
            self.toggle_animation.setDirection(direction)
            self.toggle_animation.start()

        self.toggle_button.clicked.connect(start_animation)

    def set_content_layout(self, content_layout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.content_area.destroy()
        self.content_area.setLayout(content_layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = content_layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()-1):
            spoiler_animation = self.toggle_animation.animationAt(i)
            spoiler_animation.setDuration(self.animation_duration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)
        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(self.animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)
