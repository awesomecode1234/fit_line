import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QWidget, QLabel, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)
from matplotlib.figure import Figure
from fpdf import FPDF
from scipy.optimize import curve_fit
from datetime import datetime
import os

class JRCurveFitApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("J-R Curve Fit")
        self.setGeometry(100, 100, 970, 600)

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        # Main Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a group box for the curve fit results
        result_group_box = QGroupBox("Curve Fit Results")
        result_group_box.setFont(QFont("Arial", 12))  # Set font for the group box title

        # Layouts
        main_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        plot_layout = QVBoxLayout()
        result_layout = QHBoxLayout()

        # Table
        self.table = QTableWidget()
        # Set the table headers statically.
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Δa (in)", "J (in-kips/in²)"])
        
        table_layout.addWidget(self.table)

        # Buttons
        self.import_btn = QPushButton("Import Data")
        self.import_btn.clicked.connect(self.import_data)
        self.import_btn.setFixedSize(140, 40)
        self.fit_btn = QPushButton("Fit J-R")
        self.fit_btn.clicked.connect(self.fit_curve)
        self.fit_btn.setEnabled(False)
        self.fit_btn.setFixedSize(140, 40)
        self.report_btn = QPushButton("Print Report")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)
        self.report_btn.setFixedSize(140, 40)
        table_layout.addWidget(self.import_btn, alignment=Qt.AlignCenter)
        table_layout.addWidget(self.fit_btn, alignment=Qt.AlignCenter)
        table_layout.addWidget(self.report_btn, alignment=Qt.AlignCenter)

        # Plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot_axes = self.figure.add_subplot(111)
        plot_layout.addWidget(self.canvas)

        # Add the result values label to the group box
        self.result_values = QLabel("")
        self.result_values.setFont(QFont("Arial", 12))
        self.result_values.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_values)
        result_group_box.setLayout(result_layout)
        plot_layout.addWidget(result_group_box)

        # Add to Main Layout
        main_layout.addLayout(table_layout)
        main_layout.addLayout(plot_layout)
        main_widget.setLayout(main_layout)
        

    def import_data(self):
        try:
            # Disconnect signal to prevent unintended triggers
            try:
                self.table.itemChanged.disconnect(self.on_table_data_changed)
            except TypeError:
                # Handles case where no connection exists
                pass

            file_name, _ = QFileDialog.getOpenFileName(
                self, "Import Data", "", "CSV Files (*.csv);;All Files (*)"
            )
            base_name = os.path.basename(file_name)
            self.file_name_only = os.path.splitext(base_name)[0]
            print(file_name)
            if file_name:
                self.report_btn.setEnabled(False)
                # Load the file and skip the header row if present
                self.data = pd.read_csv(file_name, header=None)

                # Attempt to convert both columns to numeric values
                self.data[0] = pd.to_numeric(self.data[0], errors='coerce')
                self.data[1] = pd.to_numeric(self.data[1], errors='coerce')

                # Check if the file contains exactly two columns
                if self.data.shape[1] != 2:
                    raise ValueError("The file must contain exactly two columns.")

                # Drop rows where either column has NaN (indicating invalid data for that row)
                self.data.dropna(inplace=True)

                # Warn about invalid data conditions but continue processing
                if (self.data < 0).any().any():
                    QMessageBox.warning(self, "Warning", "All data values must be ≥ 0.")
                if not self.data[0].is_monotonic_increasing or not self.data[1].is_monotonic_increasing:
                    QMessageBox.warning(self, "Warning", "Data must be in ascending order.")

                # Display data in the table
                self.display_data()

                # Plot the imported data
                self.plot_data_only()

                # Enable the Fit J-R button
                self.fit_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Invalid File", f"Error: {str(e)}")

        finally:
            # Reconnect the signal after processing
            self.table.itemChanged.connect(self.on_table_data_changed)



    def on_table_data_changed(self, item):
        """
        Handles the event when a cell in the table is manually edited.
        Resets the state of the application.
        """
        try:
            # Validate that the edited value is numeric and non-negative
            if item and item.text():
                value = float(item.text())
                if value < 0:
                    raise ValueError("Value must be non-negative.")
            else:
                raise ValueError("Cell cannot be empty.")

            # Reset the plot (clear any fitted line)
            self.plot_data_only()

            # Disable the Print Report button and enable the Fit J-R button
            self.report_btn.setEnabled(False)
            self.fit_btn.setEnabled(True)

        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid non-negative numeric value.")
            # Reset the invalid cell to a default value of 0.0
            item.setText("0.0")




    def plot_data_only(self):
        self.plot_axes.clear()

        # Initialize data lists
        da = []
        j = []

        # Read data from the table
        for row in range(self.table.rowCount()):
            try:
                # Safely handle empty or invalid cells by defaulting to 0.0
                da_value = float(self.table.item(row, 0).text() if self.table.item(row, 0) else "0.0")
                j_value = float(self.table.item(row, 1).text() if self.table.item(row, 1) else "0.0")
                if da_value < 0 or j_value < 0:
                    raise ValueError("Values must be non-negative.")
                da.append(da_value)
                j.append(j_value)
            except ValueError:
                QMessageBox.warning(self, "Invalid Data", f"Invalid or negative data at row {row + 1}. Defaulting to 0.0.")
                da.append(0.0)
                j.append(0.0)

        # Plot the valid data points
        self.plot_axes.plot(da, j, 'bo', label="Data", markersize=8, markeredgewidth=2, markeredgecolor='black')

        # Set labels and grid
        self.plot_axes.set_xlabel("Δa (in)", fontsize=12)
        self.plot_axes.set_ylabel("J (in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')

        # Set axis limits with margins
        self.plot_axes.set_xlim(0, max(da) + 0.02 if da else 0.1)
        self.plot_axes.set_ylim(0, max(j) + 1 if j else 0.1)

        # Update the canvas
        self.canvas.draw()



    def display_data(self):
        self.table.setRowCount(len(self.data))
        self.table.setHorizontalHeaderLabels(["Δa (in)", "J (in-kips/in²)"])  # Ensure headers are fixed

        for i, (da, j) in enumerate(zip(self.data.iloc[:, 0], self.data.iloc[:, 1])):
            item_da = QTableWidgetItem(f"{da:.4f}")
            item_j = QTableWidgetItem(f"{j:.4f}")
            
            # Set right alignment for the numbers
            item_da.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_j.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Allow editing
            item_da.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_j.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            
            self.table.setItem(i, 0, item_da)
            self.table.setItem(i, 1, item_j)



    def fit_curve(self):
        try:
            # Extract data from the table
            rows = self.table.rowCount()
            da = []
            j = []
            for row in range(rows):
                da_value = float(self.table.item(row, 0).text())
                j_value = float(self.table.item(row, 1).text())
                da.append(da_value)
                j.append(j_value)

            da = np.array(da)
            j = np.array(j)

            # Perform validations
            if len(da) < 2 or len(j) < 2:
                raise ValueError("The data must contain at least two rows.")
            if not (da >= 0).all() or not (j >= 0).all():
                raise ValueError("All values in the data must be greater than or equal to zero.")
            if not (np.diff(da) >= 0).all() or not (np.diff(j) >= 0).all():
                raise ValueError("Data in both columns must be in ascending order.")

            # Fit Function: J = C * (Δa)^m
            def jr_curve(delta_a, C, m):
                return C * (delta_a ** m)

            popt, _ = curve_fit(jr_curve, da, j)
            C, m = popt
            # Display Results
            self.result_values.setText(f"C = {C:.2f}               m = {m:.2f}")
            self.plot_data_with_fit(da, j, jr_curve, popt)
            self.fit_params = (C, m)
            self.report_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Invalid Data", f"Error: {str(e)}")

    def plot_data_with_fit(self, da, j, jr_curve, popt):
        self.plot_axes.clear()

        # Plot the original data points (scatter plot)
        self.plot_axes.plot(da, j, 'bo', label="Data", markersize=8, markeredgewidth=2, markeredgecolor='black')

        # Generate a fine grid for Δa to plot a smooth curve
        da_fine = np.linspace(da.min(), da.max(), 500)
        self.plot_axes.plot(da_fine, jr_curve(da_fine, *popt), 'r-', label="Fit", linewidth=2)

        # Set labels and grid
        self.plot_axes.set_xlabel("Δa (in)", fontsize=12)
        self.plot_axes.set_ylabel("J (in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')

        # Set axis limits with margins
        self.plot_axes.set_xlim(0, da.max() + 0.02)
        self.plot_axes.set_ylim(0, max(j.max(), jr_curve(da.max(), *popt)) + 1)

        # Add legend
        self.plot_axes.legend(loc="upper left", fontsize=10)

        # Update the canvas
        self.canvas.draw()

    def plot_curve(self, da, j, jr_curve, popt):
        self.plot_axes.clear()

        # Plot the original data points with a more distinct style (blue circles)
        self.plot_axes.plot(da, j, 'bo', label="Data", markersize=8, markeredgewidth=2, markeredgecolor='black')

        # Generate a fine grid for Δa to plot a smooth curve
        da_fine = np.linspace(da.min(), da.max(), 500)
        self.plot_axes.plot(da_fine, jr_curve(da_fine, *popt), 'r-', label="Fit", linewidth=2)

        # Set labels for axes with better font size
        self.plot_axes.set_xlabel("Δa (in)", fontsize=12)
        self.plot_axes.set_ylabel("J (in-kips/in²)", fontsize=12)

        # Set the axis limits to focus the plot more around the data
        self.plot_axes.set_xlim(0, da.max() + 0.02)  # Adding a bit of margin to the right of the data
        self.plot_axes.set_ylim(0, max(j.max(), jr_curve(da.max(), *popt)) + 1)  # Adding some margin on top

        # Increase grid line visibility
        self.plot_axes.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

        # Make ticks on both axes more visible
        self.plot_axes.tick_params(axis='both', which='major', labelsize=10, width=2)

        # Adding legend
        self.plot_axes.legend(loc="upper left", fontsize=10)

        # Set background color for the plot
        self.plot_axes.set_facecolor('white')

        # Update the canvas with new plot
        self.canvas.draw()


    def generate_report(self):
        # Prompt user to select or enter a file name
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Optional: Remove this if native dialog is preferred
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Report As", self.file_name_only + ".pdf", "PDF Files (*.pdf);;All Files (*)", options=options
        )
        
        if file_name:
            # Ensure the file has a ".pdf" extension
            if not file_name.endswith(".pdf"):
                file_name += ".pdf"

            # Check if the file already exists
            if os.path.exists(file_name):
                # Show a warning dialog about overwriting
                reply = QMessageBox.question(
                    self, "Overwrite File",
                    f"The file '{file_name}' already exists. Do you want to overwrite it?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return  # Exit without saving if user chooses not to overwrite

            # Save the plot as an image
            plot_image_file = "jr_curve_plot.png"
            self.figure.savefig(plot_image_file, bbox_inches="tight", dpi=300)

            # Initialize the PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Title Section
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(0, 10, "JRFit V1.0", ln=True, align="C")
            pdf.ln(10)

            # Add Date
            current_date = datetime.now().strftime("%B %d, %Y  %I:%M %p")
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Date: {current_date}", ln=True)
            pdf.ln(10)

            # Input File Name (just a placeholder in this case)
            input_file_name = self.file_name_only + ".csv"  # Replace with actual filename if dynamically loaded
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Input File: {input_file_name}", ln=True)
            pdf.ln(10)

            # Input Data Table - Header
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(40, 10, "Delta a (in)", border=1, align="C")  # First column header
            pdf.cell(50, 10, "J (in-kips/in²)", border=1, align="C")  # Second column header
            pdf.ln()  # Line break after the header row

            # Add Data Rows from the table (not from self.data)
            pdf.set_font("Arial", size=12)
            for row in range(self.table.rowCount()):
                da_value = self.table.item(row, 0).text() if self.table.item(row, 0) else "0.0"
                j_value = self.table.item(row, 1).text() if self.table.item(row, 1) else "0.0"
                pdf.cell(40, 10, f"{da_value}", border=1, align="C")  # Δa value
                pdf.cell(50, 10, f"{j_value}", border=1, align="C")  # J value
                pdf.ln()  # Line break after each row

            # Curve Fit Results Section
            pdf.ln(10)
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, "Curve Fit Results:", ln=True)
            pdf.ln(5)

            C, m = self.fit_params
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"C = {C:.2f}", ln=True)
            pdf.cell(0, 10, f"m = {m:.2f}", ln=True)

            # Add the Plot Image
            pdf.ln(10)
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, "J-R Curve Plot:", ln=True)
            pdf.ln(5)
            pdf.image(plot_image_file, x=30, y=None, w=150)  # Adjust image position and size

            # Save the PDF File
            pdf.output(file_name)

            # Indicate the report has been saved
            QMessageBox.information(self, "Report Saved", f"Report has been saved as '{file_name}'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = JRCurveFitApp()
    main_win.show()
    sys.exit(app.exec_())
