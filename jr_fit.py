import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from fpdf import FPDF
from scipy.optimize import curve_fit
import os
from datetime import datetime


class JR_Fit_Dialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.file_list = []
        self.result = None  # To store the selected files
        self.setup_ui()
        self.result = None
        # Make modal
        self.grab_set()
        self.transient(parent)
        self.wait_window(self)

    def setup_ui(self):
        self.title("J-R Curve Fit")
        self.geometry("1080x700")

        # Main Frame
        main_frame = ttk.Frame(self)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Table Frame
        table_frame = ttk.Frame(main_frame, width=130)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_frame.pack_propagate(False)

        # Plot Frame
        plot_frame = ttk.Frame(main_frame, width=400, padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Table
        self.table = ttk.Treeview(table_frame, columns=("No", "Delta_a", "J"), show="headings", height=15)
        self.table.heading("No", text="No",anchor="w")
        self.table.heading("Delta_a", text="Δa(in)", anchor="w")
        self.table.heading("J", text="J(in-kips/in²)",anchor="w")
        self.table.column("No", width=10)  # Width for the "No" column
        self.table.column("Delta_a", width=60)  # Width for the "Delta_a" column
        self.table.column("J", width=60)  # Width for the "J" column
        self.table.pack(side=tk.TOP, fill=tk.BOTH, expand = 1)

        # Buttons
        button_frame = ttk.Frame(table_frame)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        import_button = ttk.Button(button_frame, text="   Import Data   ", command=self.import_data)
        import_button.grid(row=0, column=0, padx=30, pady=5)

        self.fit_button = ttk.Button(button_frame, text="        Fit J-R        ", command=self.fit_curve, state=tk.DISABLED)
        self.fit_button.grid(row=1, column=0, padx=30, pady=5)

        self.report_button = ttk.Button(button_frame, text="   Print Report   ", command=self.generate_report, state=tk.DISABLED)
        self.report_button.grid(row=2, column=0, padx=30, pady=5)

        close_button = ttk.Button(button_frame, text="         Close        ", command=self.destroy)
        close_button.grid(row=3, column=0, padx=30, pady=5)

        # Plot
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot_axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=6)

        # Results Label
        self.result_label_frame = ttk.LabelFrame(plot_frame, text="Curve Fit Results")
        self.result_label = ttk.Label(self.result_label_frame, text="", font=("Arial", 12))
        self.result_label.pack(padx=10, pady=10)
        self.result_label_frame.pack(fill = tk.X, side=tk.BOTTOM, pady=10)

        
    def import_data(self):
        file_name = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_name:
            try:
                self.data = pd.read_csv(file_name, header=0, dtype={0: float, 1: float})
                if self.data.shape[1] != 2:
                    raise ValueError("The file must contain exactly two columns.")
                self.data.dropna(inplace=True)
                self.display_data()
                self.plot_data_only()
                self.fit_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Invalid File", f"Error: {str(e)}")

    def display_data(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for index, (da, j) in enumerate(self.data.values):
            self.table.insert("", "end", values=(index+1, da, j))

    def plot_data_only(self):
        self.plot_axes.clear()
        da, j = self.data.iloc[:, 0], self.data.iloc[:, 1]
        self.plot_axes.plot(da, j, 'bo', markersize=8, markeredgewidth=2, markeredgecolor='black')
        self.plot_axes.set_xlabel("Δa(in)", fontsize=12)
        self.plot_axes.set_ylabel("J(in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')
        self.canvas.draw()

    def fit_curve(self):
        try:
            da = self.data.iloc[:, 0].values
            j = self.data.iloc[:, 1].values
            da1 = da[1:]
            j1 = j[1:]

            def jr_curve(delta_a, C, m):
                return C * np.power(delta_a, m)

            popt, _ = curve_fit(jr_curve, da1, j1)
            C, m = popt
            self.result = (C, m)
            self.result_label.config(text=f"C = {C:.2f}   m = {m:.2f}")
            self.plot_data_with_fit(da, j, jr_curve, popt)
            self.fit_params = (C, m)
            self.report_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Invalid Data", f"Error: {str(e)}")

    def plot_data_with_fit(self, da, j, jr_curve, popt):
        self.plot_axes.clear()
        self.plot_axes.plot(da, j, 'bo', markersize=8, markeredgewidth=2, markeredgecolor='black', label = "Data")
        da_fine = np.linspace(da.min(), da.max(), 500)
        self.plot_axes.plot(da_fine, jr_curve(da_fine, *popt), 'r-', linewidth=2, label = "Fit")
        self.plot_axes.set_xlabel("Δa(in)", fontsize=12)
        self.plot_axes.set_ylabel("J(in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')
        self.plot_axes.legend(fontsize=10)
        self.canvas.draw()

    def generate_report(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf")],
                                                 initialfile="report")
        if file_name:
            plot_image_file = "jr_curve_plot.png"
            self.figure.savefig(plot_image_file, bbox_inches="tight", dpi=300)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, "JRFit V1.0", ln=True, align="C")
            pdf.ln(10)
            current_date = datetime.now().strftime("%B %d, %Y  %I:%M %p")
            pdf.cell(0, 10, f"Date: {current_date}", ln=True)
            pdf.ln(10)
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(40, 10, "Delta a (in)", border=1, align="C")
            pdf.cell(50, 10, "J (in-kips/in²)", border=1, align="C")
            pdf.ln()
            pdf.set_font("Arial", size=12)
            for row_id in self.table.get_children():
                row = self.table.item(row_id)['values']
                pdf.cell(40, 10, f"{float(row[1]):.4f}", border=1, align="C")
                pdf.cell(50, 10, f"{float(row[2]):.4f}", border=1, align="C")
                pdf.ln()
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, "Curve Fit Results:", ln=True)
            pdf.ln(5)
            C, m = self.fit_params
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"C = {C:.2f}", ln=True)
            pdf.cell(0, 10, f"m = {m:.2f}", ln=True)
            pdf.ln(10)
            pdf.image(plot_image_file, x=30, w=150)
            pdf.output(file_name)
            messagebox.showinfo("Report Saved", f"Report has been saved as '{file_name}'")


