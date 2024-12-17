import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from fpdf import FPDF
from scipy.optimize import curve_fit
import os
from datetime import datetime

class JRCurveFitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PREVENTURE")
        self.root.geometry("1080x720")
        self.root.configure(bg='lightgray')

        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Anaylysis")
        file_menu.add_command(label="Open Analysis")
        file_menu.add_separator()
        file_menu.add_command(label="Save Inputs")
        file_menu.add_command(label="Save Inputs As...")
        file_menu.add_command(label="Save Outputs")
        file_menu.add_command(label="Save Outputs as ...")
        file_menu.add_separator()
        file_menu.add_command(label="Close Analysis")
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        calculate_menu = tk.Menu(menubar, tearoff=0)
        # calculate_menu.add_command(label="Calculate J-R", command=self.calculate_jr)
        calculate_menu.add_command(label="Calculate Stress")
        menubar.add_cascade(label="Calculate", menu=calculate_menu)

        batchrun_menu = tk.Menu(menubar, tearoff=0)
        batchrun_menu.add_command(label="Batch Run")
        menubar.add_cascade(label="Batch Run", menu=batchrun_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About")
        menubar.add_cascade(label="About", menu=about_menu)

        root.config(menu=menubar)

        
        # Left Frame: Input Panel
        input_frame = ttk.Frame(root)
        input_frame.grid(row = 1, column =0, padx=10, pady=10)

        # Main Frame
        first_col = ttk.Frame(input_frame, width = 200)
        first_col.grid(row=1, column =0, padx=10, pady=10)

        toolbar_frame = tk.Frame(input_frame)
        toolbar_frame.grid(row =0, column =0, sticky="nw",padx=10, pady=5)
        
        new_image =   PhotoImage(file="new.png")
        open_image = PhotoImage(file="open.png")
        save_image = PhotoImage(file="save.png")
        run_image = PhotoImage(file="run.png")
        run2_image = PhotoImage(file="run2.png")
        
        new_button = Button(toolbar_frame, image=new_image, command=lambda: print("Open button clicked"))
        new_button.image = new_image
        new_button.pack(side=tk.LEFT)

        open_button = Button(toolbar_frame, image=open_image, command=lambda: print("Open button clicked"))
        open_button.image = open_image
        open_button.pack(side=tk.LEFT)

        save_button = Button(toolbar_frame, image=save_image, command=lambda: print("save button clicked"))
        save_button.image = save_image
        save_button.pack(side=tk.LEFT)
        
        run_button = Button(toolbar_frame, image=run_image, command=lambda: print("run button clicked"))
        run_button.image = run_image
        run_button.pack(side=tk.LEFT)

        run2_button = Button(toolbar_frame, image=run2_image, command=lambda: print("run2 button clicked"))
        run2_button.image = run2_image
        run2_button.pack(side=tk.LEFT)

        pipe_frame = ttk.LabelFrame(first_col, text="Pipe & Loads", padding="10")
        pipe_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        fields = [
            ("Nominal Pipe Size (in)", "12"), 
            ("Pipe OD (in)", "12"), 
            ("Wall Thickness (in)", "0.5"),
            ("Pressure (psi)", "2250"), 
            ("Temperature (°F)", "600"), 
            ("Max. Op. Stress (ksi)", "15")
        ]

        for i, (label, default) in enumerate(fields):
            ttk.Label(pipe_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(pipe_frame, width=10)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=2)

        # BAC section
        bac_frame = ttk.LabelFrame(first_col, text="BAC", padding="10")
        bac_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        ttk.Label(bac_frame, text="Max. Op. Stress (ksi)").grid(row=0, column=0, sticky="w", padx=5)
        bac_entry = ttk.Entry(bac_frame, width=10)
        bac_entry.insert(0, "55")
        bac_entry.grid(row=0, column=1)

        ttk.Label(bac_frame, text="No. of Points").grid(row=1, column=0, sticky="w", padx=5)
        bac_entry = ttk.Entry(bac_frame, width=10)
        bac_entry.insert(0, "15")
        bac_entry.grid(row=1, column=1)

        # Radio Buttons
        bac_option = tk.StringVar(value="Biased")
        ttk.Radiobutton(bac_frame, text="Equidistant", variable=bac_option, value="Equidistant").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(bac_frame, text="Biased", variable=bac_option, value="Biased").grid(row=2, column=1, sticky="w")

        options = ["1-ASME SA-106 Gr C", "2-ASME SA-312(Type 304/304L)", "3-ASME SA-106 Gr B", "4-ASME SA-335 Gr P11", "5-User Defined"]
        variable = tk.StringVar(root)
        variable.set(options[2])  # default value
        optionmenu = tk.OptionMenu(first_col, variable, *options)
        optionmenu.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        # menubutton = Menubutton(first_col, text="2-ASME SA-312(Type 304/304L)")
        # menubutton.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        # menu = Menu(menubutton, tearoff=0)
        # menu.add_command(label="1-ASME SA-106 Gr C")
        # menu.add_command(label="2-ASME SA-312(Type 304/304L)")
        # menubutton.config(menu=menu)

        # tensile_frame = ttk.LabelFrame(main_frame, text="2 - ASME SA-312 (Type 304/304L)", padding="10")
        tensile_frame = ttk.LabelFrame(first_col, text="Tensile Properties", padding="10")

        tensile_frame.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        tensile_fields = [
            ("Yield Strength (ksi)", "30"), 
            ("UTS (ksi)", "60"),
            ("Elastic Modulus (ksi)", "28000"),
            ("RO Alpha", "0.5"), 
            ("RO n", "3.5")
        ]
        for i, (label, default) in enumerate(tensile_fields):
            ttk.Label(tensile_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(tensile_frame, width=10)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=2)

        # Buttons
        ttk.Button(first_col, text="Fit R-O Curve from Stress-Strain Data").grid(row=4, column=0, pady=5)
        ttk.Button(first_col, text="      Fit R-O Curve from YS-UTS      ").grid(row=5, column=0, pady=5)

        # ========== Section 3: Crack Morphology ==========
        second_col = ttk.Frame(input_frame)
        second_col.grid(row=1, column=1, sticky="nw", padx=10, pady=10)
        crack_frame = ttk.LabelFrame(second_col, text="Crack Morphology", padding="10")
        crack_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        CrackMorphology = tk.StringVar(value="CrackMorphology")

        options = [
            "IGSCC", "PWSCC Weld", "User-Defined", 
        ]
        for i, opt in enumerate(options):
            ttk.Radiobutton(crack_frame, text=opt, variable=CrackMorphology, value=opt).grid(row=i, column=0, sticky="w", pady=2)

        options = [ 
            "Cor. Fatigue", "Fatigue"
        ]

        
        for i, opt in enumerate(options):
            ttk.Radiobutton(crack_frame, text=opt, variable=CrackMorphology, value=opt).grid(row=i, column=1, sticky="w", pady=2)

        ttk.Label(crack_frame, text="45 Degree Turns").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(crack_frame, width=10)
        entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(crack_frame, text="Roughness").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(crack_frame, width=10)
        entry.grid(row=4, column=1, padx=5, pady=2)

        GPM_frame = ttk.LabelFrame(second_col, text="Detectable Leak Rates (GPM)", padding="10")
        GPM_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        leak_rates = ["0.05", "0.1", "0.25", "0.5", "1.0"]
        for i, rate in enumerate(leak_rates):
            ttk.Radiobutton(GPM_frame, text=rate, value=rate).grid(row=0, column=i, sticky="w")

        # Fracture Toughness
        fracture_frame = ttk.LabelFrame(second_col, text="Fracture Toughness", padding="10")
        fracture_frame.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(fracture_frame, text="Coef. C (-1/R):").grid(row=0, column=0, sticky="w")
        c_entry = ttk.Entry(fracture_frame, width=10)
        c_entry.insert(0, "1.5")
        c_entry.grid(row=0, column=1, padx=5)

        ttk.Label(fracture_frame, text="Exponent m:").grid(row=1, column=0, sticky="w")
        m_entry = ttk.Entry(fracture_frame, width=10)
        m_entry.insert(0, "0.43")
        m_entry.grid(row=1, column=1, padx=5)

        ttk.Button(fracture_frame, text="Fit J-R Curve from Data").grid(row=3, column=0, columnspan=2, pady=5)

        # ========== Section 4: Failure Criteria ==========
        failure_frame = ttk.LabelFrame(second_col, text="Failure Criteria", padding="10")
        failure_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        failure_option = tk.StringVar(value="Limit Load")
        ttk.Radiobutton(failure_frame, text="Limit Load", variable=failure_option, value="Limit Load").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(failure_frame, text="EPFM", variable=failure_option, value="EPFM").grid(row=0, column=1, sticky="w")

        
        # ========== Section 5: Output ==========
        # Table Frame
        table_frame = ttk.Frame(input_frame)
        table_frame.grid(row=1, column=2, padx=10, pady=10)

        # Plot Frame
        plot_frame = ttk.Frame(input_frame, width =300)
        plot_frame.grid(row=1, column =2, padx=10, pady=10)

        # Table
        self.table = ttk.Treeview(table_frame, columns=("Delta_a", "J"), show="headings", height=15)
        self.table.heading("Delta_a", text="Δa (in)")
        self.table.heading("J", text="J (in-kips/in²)")
        self.table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = ttk.Frame(table_frame)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        import_button = ttk.Button(button_frame, text="Import Data", command=self.import_data)
        import_button.grid(row=0, column=0, padx=10)

        self.fit_button = ttk.Button(button_frame, text="Fit J-R Curve from Data", command=self.fit_curve, state=tk.DISABLED)
        self.fit_button.grid(row=0, column=1, padx=10)



        self.report_button = ttk.Button(button_frame, text="Print Report", command=self.generate_report, state=tk.DISABLED)
        self.report_button.grid(row=0, column=2, padx=10)

        # Plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot_axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Results Label
        self.result_label = ttk.Label(plot_frame, text="", font=("Arial", 12))
        self.result_label.pack(side=tk.BOTTOM, pady=10)

    def import_data(self):
        file_name = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_name:
            try:
                self.data = pd.read_csv(file_name, header=None, dtype={0: float, 1: float})
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
        for index, (da, j) in self.data.iterrows():
            self.table.insert("", "end", values=(da, j))

    def plot_data_only(self):
        self.plot_axes.clear()
        da, j = self.data.iloc[:, 0], self.data.iloc[:, 1]
        self.plot_axes.plot(da, j, 'bo', markersize=8, markeredgewidth=2, markeredgecolor='black')
        self.plot_axes.set_xlabel("Δa (in)", fontsize=12)
        self.plot_axes.set_ylabel("J (in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')
        self.canvas.draw()

    def fit_curve(self):
        try:
            da = self.data.iloc[:, 0].values
            j = self.data.iloc[:, 1].values

            def jr_curve(delta_a, C, m):
                return C * (delta_a ** m)

            popt, _ = curve_fit(jr_curve, da, j)
            C, m = popt
            self.result_label.config(text=f"C = {C:.2f}   m = {m:.2f}")
            self.plot_data_with_fit(da, j, jr_curve, popt)
            self.fit_params = (C, m)
            self.report_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Invalid Data", f"Error: {str(e)}")

    def plot_data_with_fit(self, da, j, jr_curve, popt):
        self.plot_axes.clear()
        self.plot_axes.plot(da, j, 'bo', markersize=8, markeredgewidth=2, markeredgecolor='black')
        da_fine = np.linspace(da.min(), da.max(), 500)
        self.plot_axes.plot(da_fine, jr_curve(da_fine, *popt), 'r-', linewidth=2)
        self.plot_axes.set_xlabel("Δa (in)", fontsize=12)
        self.plot_axes.set_ylabel("J (in-kips/in²)", fontsize=12)
        self.plot_axes.grid(True, linestyle='--', linewidth=0.5, color='gray')
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
                pdf.cell(40, 10, f"{row[0]:.4f}", border=1, align="C")
                pdf.cell(50, 10, f"{row[1]:.4f}", border=1, align="C")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = JRCurveFitApp(root)
    root.mainloop()
