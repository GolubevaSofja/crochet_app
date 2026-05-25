# all elements used in the graphical interface, imports of PySide6 elements
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from calculations import CrochetSurfaceCalculator
from visualization import CrochetMeshViewer


class MainWindow(QMainWindow):
    DEFAULT_ROUNDNESS = 0.70
    DEFAULT_END_ROUNDNESS = 0.90

    def __init__(self):
        super().__init__()

        # window title and width
        self.setWindowTitle("Crochet Shape Visualizer")
        self.setMinimumSize(1100, 700)

        # main container for the interface
        main_widget = QWidget()
        # horizontal layout for the elements
        main_layout = QHBoxLayout(main_widget)

        # creation of two parts of the window - left and right
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        # adding parts to the window
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.setCentralWidget(main_widget)

        # adding default rows and building the model
        self.add_default_rows()
        self.build_model()

    # Method for creating the left panel of the interface
    # This panel contains fields for inputting the stitch width and row height
    # A table with the rows of the project and buttons for managing the application
    def create_left_panel(self):
        panel = QWidget()
        # vertical layout of elements
        layout = QVBoxLayout(panel)

        title = QLabel("Parameters")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.measurement_mode_input = QComboBox()
        self.measurement_mode_input.addItems([
            "One stitch and one row",
            "Sample width and height",
        ])

        self.parameter_pages = QStackedWidget()
        self.parameter_pages.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum,
        )

        self.stitch_width_input = QDoubleSpinBox()
        self.stitch_width_input.setRange(0.01, 10.00)
        self.stitch_width_input.setSingleStep(0.01)
        self.stitch_width_input.setValue(0.75)
        self.stitch_width_input.setSuffix(" cm")

        self.row_height_input = QDoubleSpinBox()
        self.row_height_input.setRange(0.01, 10.00)
        self.row_height_input.setSingleStep(0.01)
        self.row_height_input.setValue(0.73)
        self.row_height_input.setSuffix(" cm")

        direct_parameters = QWidget()
        direct_form_layout = QFormLayout(direct_parameters)
        direct_form_layout.addRow("Stitch width:", self.stitch_width_input)
        direct_form_layout.addRow("Row height:", self.row_height_input)

        self.sample_width_input = QDoubleSpinBox()
        self.sample_width_input.setRange(0.01, 1000.00)
        self.sample_width_input.setSingleStep(0.10)
        self.sample_width_input.setValue(7.50)
        self.sample_width_input.setSuffix(" cm")

        self.sample_height_input = QDoubleSpinBox()
        self.sample_height_input.setRange(0.01, 1000.00)
        self.sample_height_input.setSingleStep(0.10)
        self.sample_height_input.setValue(2.92)
        self.sample_height_input.setSuffix(" cm")

        self.sample_stitches_input = QSpinBox()
        self.sample_stitches_input.setRange(1, 10000)
        self.sample_stitches_input.setValue(10)

        self.sample_rows_input = QSpinBox()
        self.sample_rows_input.setRange(1, 10000)
        self.sample_rows_input.setValue(4)

        sample_parameters = QWidget()
        sample_form_layout = QFormLayout(sample_parameters)
        sample_form_layout.addRow("Row length:", self.sample_width_input)
        sample_form_layout.addRow("Stitches in row:", self.sample_stitches_input)
        sample_form_layout.addRow("Sample height:", self.sample_height_input)
        sample_form_layout.addRow("Rows in sample:", self.sample_rows_input)

        self.parameter_pages.addWidget(direct_parameters)
        self.parameter_pages.addWidget(sample_parameters)
        self.measurement_mode_input.currentIndexChanged.connect(
            self.parameter_pages.setCurrentIndex
        )

        self.rows_table = QTableWidget()
        self.rows_table.setColumnCount(2)
        self.rows_table.setHorizontalHeaderLabels(["Row", "Stitches"])
        self.rows_table.setRowCount(0)

        self.add_row_button = QPushButton("Add row")
        self.delete_row_button = QPushButton("Delete selected row")
        self.build_button = QPushButton("Build 3D model")
        self.build_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.pattern_button = QPushButton("Show row scheme")
        self.instructions_button = QPushButton("Instructions")

        self.add_row_button.clicked.connect(self.add_row)
        self.delete_row_button.clicked.connect(self.delete_selected_row)
        self.build_button.clicked.connect(self.build_model)
        self.pattern_button.clicked.connect(self.show_row_scheme)
        self.instructions_button.clicked.connect(self.show_instructions)

        layout.addWidget(self.instructions_button)
        layout.addWidget(title)
        layout.addWidget(QLabel("Parameter input:"))
        layout.addWidget(self.measurement_mode_input)
        layout.addWidget(self.parameter_pages)
        layout.addWidget(QLabel("Rows:"))
        layout.addWidget(self.rows_table)
        layout.addWidget(self.add_row_button)
        layout.addWidget(self.delete_row_button)
        layout.addWidget(self.pattern_button)
        layout.addWidget(self.build_button)

        return panel

    # Method for creating the right panel of the interface
    # This panel contains the preview area for the 3D model
    # The actual rendering of the model is handled by the CrochetMeshViewer class
    def create_right_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(panel)

        title = QLabel("3D model preview")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.viewer = CrochetMeshViewer(panel)

        layout.addWidget(title)
        layout.addWidget(self.viewer.widget)

        return panel

    # The method adds a predefined set of rows to the table
    # These rows are used as an example so that, when the application starts, the user immediately sees a generated 3D model
    def add_default_rows(self):
        # default_stitches = [6, 12, 18, 24, 30, 36, 42, 48, 48, 48, 48, 48, 48, 48, 48, 42, 36, 30, 24, 18, 18, 24, 30, 36, 42, 48, 48, 48, 48, 48, 48, 48, 42, 36, 30, 24, 18, 12, 6,]
        # 1 and 2
        # default_stitches = [6, 12, 18, 24, 24, 24, 24, 24, 24, 18, 12, 6]

        # 3
        # default_stitches = [6, 12, 18, 24, 30, 36, 42, 48, 48, 48, 48, 48, 48, 48, 48, 42, 36, 30, 24, 18, 12, 6]
        
        # 4
        # default_stitches = [6, 12, 18, 24, 30, 36, 42, 48, 48, 48, 48, 48, 48, 48, 48, 42, 36, 30, 24, 18, 18, 24, 30, 36, 42, 48, 48, 48, 48, 48, 48, 48, 48, 42, 36, 30, 24, 18, 12, 6]
        
        # 5
        default_stitches = [6, 12, 18, 24, 30, 36, 42, 48, 48, 48, 48, 42, 36, 36, 42, 48, 48, 48, 48, 42, 36, 30, 24, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 12, 6]
        

        for stitches in default_stitches:
            self.add_row(stitches)

    # Method for adding a new row to the rows table
    # The first column contains the row number, and the second column contains the number of stitches in that row
    # If no value is provided, a row with 6 stitches is added by default
    def add_row(self, stitches=6):
        row_index = self.rows_table.rowCount()
        self.rows_table.insertRow(row_index)

        row_number_item = QTableWidgetItem(str(row_index + 1))
        stitches_item = QTableWidgetItem(str(stitches))

        self.rows_table.setItem(row_index, 0, row_number_item)
        self.rows_table.setItem(row_index, 1, stitches_item)

    # The method removes the row selected by the user from the table
    # After the row is removed, the row numbers are recalculated, and the 3D model is rebuilt automatically
    def delete_selected_row(self):
        selected_row = self.rows_table.currentRow()

        if selected_row >= 0:
            self.rows_table.removeRow(selected_row)
            self.renumber_rows()
            self.build_model()

    # Method for renumbering the rows in the first column of the table
    # This is needed after deleting a row to keep the numbering sequential
    def renumber_rows(self):
        for row_index in range(self.rows_table.rowCount()):
            self.rows_table.setItem(
                row_index,
                0,
                QTableWidgetItem(str(row_index + 1)),
            )

    # Method for reading data from the rows table
    # It iterates through all rows, takes the number of stitches from the second column and checks 
    # that the value is a positive integer
    # If there is an error in the table, a warning is displayed and the method returns an empty list
    def get_rows_data(self):
        stitches_per_row = []

        for row_index in range(self.rows_table.rowCount()):
            item = self.rows_table.item(row_index, 1)

            if item is None:
                continue

            try:
                stitches = int(item.text())

                if stitches <= 0:
                    raise ValueError

                if stitches_per_row:
                    previous_stitches = stitches_per_row[-1]
                    min_stitches = previous_stitches / 2
                    max_stitches = previous_stitches * 2

                    if (
                        stitches < min_stitches
                        or stitches > max_stitches
                    ):
                        QMessageBox.warning(
                            self,
                            "Input error",
                            (
                                f"Row {row_index + 1} must contain from "
                                f"{min_stitches:g} to {max_stitches:g} "
                                f"stitches."
                            ),
                        )
                        return []

                stitches_per_row.append(stitches)

            except ValueError:
                QMessageBox.warning(
                    self,
                    "Input error",
                    f"Row {row_index + 1} must contain a positive integer.",
                )
                return []

        return stitches_per_row

    # The method builds a 3D model based on the data entered by the user
    # First, it gets the stitch counts by rows from the table, then reads the stitch width and row height,
    # passes this data to the calculation class CrochetSurfaceCalculator, receives the finished model mesh,
    # and sends it to CrochetMeshViewer for display
    def build_model(self):
        stitches_per_row = self.get_rows_data()

        if len(stitches_per_row) < 2:
            QMessageBox.warning(
                self,
                "Input error",
                "At least two rows are required to build a 3D surface.",
            )
            return

        stitch_width, row_height = self.get_size_parameters()

        calculator = CrochetSurfaceCalculator(
            stitches_per_row=stitches_per_row,
            stitch_width=stitch_width,
            row_height=row_height,
            visual_roundness=self.DEFAULT_ROUNDNESS,
            end_roundness_strength=self.DEFAULT_END_ROUNDNESS,
            narrowing_sensitivity=0.85,
            min_inner_roundness=0.20,
            segments=None,
            profile_count=None,
        )
        mesh = calculator.build()

        if mesh is None:
            return

        self.viewer.display(mesh)

    # Method for showing a row-by-row crochet scheme based on the current table data
    # It displays a text instruction for each row.
    def show_row_scheme(self):
        stitches_per_row = self.get_rows_data()

        if not stitches_per_row:
            QMessageBox.warning(
                self,
                "Input error",
                "Add at least one valid row to create a row scheme.",
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Row scheme")
        dialog.setMinimumSize(420, 520)

        layout = QVBoxLayout(dialog)

        title = QLabel("Row scheme")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        scheme_table = QTableWidget()
        scheme_table.setColumnCount(2)
        scheme_table.setHorizontalHeaderLabels([
            "Row",
            "Pattern",
        ])
        scheme_table.setRowCount(len(stitches_per_row))

        for row_index, stitches in enumerate(stitches_per_row):
            scheme_table.setItem(
                row_index,
                0,
                QTableWidgetItem(str(row_index + 1)),
            )
            scheme_table.setItem(
                row_index,
                1,
                QTableWidgetItem(
                    self.row_scheme_text(stitches_per_row, row_index),
                ),
            )

        scheme_table.resizeColumnsToContents()

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(title)
        layout.addWidget(scheme_table)
        layout.addWidget(close_button)

        dialog.exec()

    # Method for creating a text instruction for one crochet row
    def row_scheme_text(self, stitches_per_row, row_index):
        current_stitches = stitches_per_row[row_index]

        if row_index == 0:
            return f"Work {current_stitches} stitches."

        previous_stitches = stitches_per_row[row_index - 1]
        stitch_difference = current_stitches - previous_stitches

        if stitch_difference == 0:
            return f"Work {current_stitches} stitches without changes."

        if stitch_difference > 0:
            increase_count = stitch_difference
            simple_stitches = current_stitches / increase_count - 2

            if simple_stitches == 0:
                return (
                    f"Work 1 increase. Repeat {increase_count} times. "
                    f"Total: {current_stitches} stitches."
                )

            return (
                f"Work {self.format_scheme_number(simple_stitches)} "
                "single crochet, then 1 increase. "
                f"Repeat {increase_count} times. "
                f"Total: {current_stitches} stitches."
            )

        decrease_count = abs(stitch_difference)
        simple_stitches = previous_stitches / decrease_count - 2

        if simple_stitches == 0:
            return (
                f"Work 1 decrease. Repeat {decrease_count} times. "
                f"Total: {current_stitches} stitches."
            )

        return (
            f"Work {self.format_scheme_number(simple_stitches)} "
            "single crochet, then 1 decrease. "
            f"Repeat {decrease_count} times. "
            f"Total: {current_stitches} stitches."
        )

    # Method for showing whole numbers without a decimal point in row scheme text
    @staticmethod
    def format_scheme_number(value):
        if float(value).is_integer():
            return str(int(value))

        return f"{value:g}"

    # Method for getting the stitch width and row height from the active parameter input mode
    # In sample mode, the app calculates the size of one stitch and one row from the measured sample.
    def get_size_parameters(self):
        if self.measurement_mode_input.currentIndex() == 1:
            stitch_width = (
                self.sample_width_input.value()
                / self.sample_stitches_input.value()
            )
            row_height = (
                self.sample_height_input.value()
                / self.sample_rows_input.value()
            )

            return stitch_width, row_height

        return (
            self.stitch_width_input.value(),
            self.row_height_input.value(),
        )

    # Method for showing instructions about using the application
    # The instructions explain what the parameters mean, how to fill the rows table, and what the main buttons are for
    def show_instructions(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Instructions")
        dialog.setMinimumSize(520, 420)

        layout = QVBoxLayout(dialog)
        text = QTextBrowser()
        text.setOpenExternalLinks(False)
        text.setHtml("""
            <h2>How to use the application</h2>
            <p>
                This app builds a simplified 3D shape from crochet rows.
                Each row in the table represents one crochet row.
            </p>

            <h3>How to enter the parameters correctly</h3>
            <ul>
                <li>First, take the yarn and hook that you are going to use to crochet the item.</li>
                <li>Crochet a small sample using this yarn and hook. It is recommended to make a sample of 10 stitches and 4 rows.</li>
                <Li>After you have crocheted this sample, measure its width and height with a ruler.</Li>
                <Li>You can enter the stitch width and row height directly, or switch the parameter input mode to sample width and height.</Li>
                <Li>In sample mode, enter the measured row length, sample height, stitches in the measured row, and rows in the sample. The app will calculate the width of one stitch and the height of one row automatically.</Li>
                <Li>The default sample values use 10 stitches in one row and 4 rows in height, but you can change both numbers.</Li>
            </ul>

            <h3>How to use the table?</h3>
            <ul>
                <li>The table already contains preliminary data. You can see that the table has 2 columns: the first column contains the row number, and the second column contains the number of stitches in the row.</li>
                <li>At the bottom, there are buttons for adding a row to the table and deleting a row.</li>
                <li>You can delete the selected cell.</li>
                <li>You can edit any entry in the table.</li>
                <li>After making changes, you need to click the button for building the visualization, and then a model based on your item data will appear.</li>
            </ul>
        """)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(text)
        layout.addWidget(close_button)

        dialog.exec()

    # The method is called when the main application window is closed
    # Before closing, it closes the 3D visualization area to properly release the used resources
    def closeEvent(self, event):
        self.viewer.close()
        event.accept()
