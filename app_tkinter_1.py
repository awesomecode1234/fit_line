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
        
        new_button = Button(toolbar_frame, image=new_image, command=self.new_analysis)
        new_button.image = new_image
        new_button.pack(side=tk.LEFT)

        open_button = Button(toolbar_frame, image=open_image, command=self.open_analysis)
        open_button.image = open_image
        open_button.pack(side=tk.LEFT)

        save_button = Button(toolbar_frame, image=save_image, command=self.save_analysis)
        save_button.image = save_image
        save_button.pack(side=tk.LEFT)
        
        run_button = Button(toolbar_frame, image=run_image, command=self.run_analysis)
        run_button.image = run_image
        run_button.pack(side=tk.LEFT)

        run2_button = Button(toolbar_frame, image=run2_image, command=self.run2_analysis)
        run2_button.image = run2_image
        run2_button.pack(side=tk.LEFT)

        pipe_frame = ttk.LabelFrame(first_col, text="Pipe & Loads", padding="10")
        pipe_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        ttk.Label(pipe_frame, text="Nominal Pipe Size (in)").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        Normal_Pipe_Size = ttk.Entry(pipe_frame, width=10)
        Normal_Pipe_Size.insert(0, 12)
        Normal_Pipe_Size.grid(row=0, column=1, padx=5, pady=2)
        self.Normal_Pipe_Size = Normal_Pipe_Size

        ttk.Label(pipe_frame, text="Pipe OD (in)").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        Pipe_OD = ttk.Entry(pipe_frame, width=10)
        Pipe_OD.insert(0, 12)
        Pipe_OD.grid(row=1, column=1, padx=5, pady=2)
        self.Pipe_OD = Pipe_OD

        ttk.Label(pipe_frame, text="Wall Thickness (in)").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        Wall_Thickness = ttk.Entry(pipe_frame, width=10)
        Wall_Thickness.insert(0, 0.5)
        Wall_Thickness.grid(row=2, column=1, padx=5, pady=2)
        self.Wall_Thickness = Wall_Thickness

        ttk.Label(pipe_frame, text="Pressure (psi)").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        Pressure = ttk.Entry(pipe_frame, width=10)
        Pressure.insert(0, 2250)
        Pressure.grid(row=3, column=1, padx=5, pady=2)
        self.Pressure = Pressure

        ttk.Label(pipe_frame, text="Temperature (°F)").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        Temperature = ttk.Entry(pipe_frame, width=10)
        Temperature.insert(0, 600)
        Temperature.grid(row=4, column=1, padx=5, pady=2)
        self.Temperature = Temperature

        ttk.Label(pipe_frame, text="Max. Op. Stress (ksi)").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        Max_Op_Stress = ttk.Entry(pipe_frame, width=10)
        Max_Op_Stress.insert(0, 15)
        Max_Op_Stress.grid(row=5, column=1, padx=5, pady=2)
        self.Max_Op_Stress = Max_Op_Stress

        # BAC section
        bac_frame = ttk.LabelFrame(first_col, text="BAC", padding="10")
        bac_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        ttk.Label(bac_frame, text="Max. Op. Stress (ksi)").grid(row=0, column=0, sticky="w", padx=5)
        BAC_Max_Op_Stress = ttk.Entry(bac_frame, width=10)
        BAC_Max_Op_Stress.insert(0, "55")
        BAC_Max_Op_Stress.grid(row=0, column=1)
        self.BAC_Max_Op_Stress = BAC_Max_Op_Stress

        ttk.Label(bac_frame, text="No. of Points").grid(row=1, column=0, sticky="w", padx=5)
        BAC_No_Of_Points = ttk.Entry(bac_frame, width=10)
        BAC_No_Of_Points.insert(0, "15")
        BAC_No_Of_Points.grid(row=1, column=1)
        self.BAC_No_Of_Points = BAC_No_Of_Points

        # Radio Buttons
        BAC_option = tk.StringVar(value="Biased")
        ttk.Radiobutton(bac_frame, text="Equidistant", variable=BAC_option, value="Equidistant").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(bac_frame, text="Biased", variable=BAC_option, value="Biased").grid(row=2, column=1, sticky="w")
        self.BAC_option = BAC_option

        options = ["1-ASME SA-106 Gr C", "2-ASME SA-312(Type 304/304L)", "3-ASME SA-106 Gr B", "4-ASME SA-335 Gr P11", "5-User Defined"]
        TypeOption= tk.StringVar(root)
        TypeOption.set(options[2])  # default value
        optionmenu = tk.OptionMenu(first_col, TypeOption, *options)
        optionmenu.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.TypeOption = TypeOption

        tensile_frame = ttk.LabelFrame(first_col, text="Tensile Properties", padding="10")

        tensile_frame.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        
        ttk.Label(tensile_frame, text="Yield Strength (ksi)").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        Yield_Strength = ttk.Entry(tensile_frame, width=10)
        Yield_Strength.insert(0, "30")
        Yield_Strength.grid(row=0, column=1, padx=5, pady=2)
        self.Yield_Strength = Yield_Strength

        ttk.Label(tensile_frame, text="UTS (ksi)").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        UTS = ttk.Entry(tensile_frame, width=10)
        UTS.insert(0, "60")
        UTS.grid(row=1, column=1, padx=5, pady=2)
        self.UTS = UTS

        ttk.Label(tensile_frame, text="Elastic Modulus (ksi)").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        Elastic_Modulus = ttk.Entry(tensile_frame, width=10)
        Elastic_Modulus.insert(0, "28000")
        Elastic_Modulus.grid(row=2, column=1, padx=5, pady=2)
        self.Elastic_Modulus = Elastic_Modulus

        ttk.Label(tensile_frame, text="RO Alpha").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        RO_Alpha = ttk.Entry(tensile_frame, width=10)
        RO_Alpha.insert(0, "4.5")
        RO_Alpha.grid(row=3, column=1, padx=5, pady=2)
        self.RO_Alpha = RO_Alpha

        ttk.Label(tensile_frame, text="RO n").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        RO_n = ttk.Entry(tensile_frame, width=10)
        RO_n.insert(0, "3.5")
        RO_n.grid(row=4, column=1, padx=5, pady=2)
        self.RO_n = RO_n

        # Buttons
        ttk.Button(first_col, text="Fit R-O Curve from Stress-Strain Data", command=self.Fit_ROCurve_from_Stress_Strain_Data).grid(row=4, column=0, pady=5)
        ttk.Button(first_col, text="      Fit R-O Curve from YS-UTS      ", command=self.Fit_ROCurve_from_YS_UTS).grid(row=5, column=0, pady=5)

        # ========== Section 3: Crack Morphology ==========
        second_col = ttk.Frame(input_frame)
        second_col.grid(row=1, column=1, sticky="nw", padx=10, pady=10)
        crack_frame = ttk.LabelFrame(second_col, text="Crack Morphology", padding="10")
        crack_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        CrackMorphology = tk.StringVar(value="Fatigue")

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

        self.CrackMorphology = CrackMorphology

        ttk.Label(crack_frame, text="45 Degree Turns").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        Degree_Turns = ttk.Entry(crack_frame, width=10)
        Degree_Turns.grid(row=3, column=1, padx=5, pady=2)
        self.Degree_Turns = Degree_Turns

        ttk.Label(crack_frame, text="Roughness").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        Roughness = ttk.Entry(crack_frame, width=10)
        Roughness.grid(row=4, column=1, padx=5, pady=2)
        self.Roughness = Roughness

        GPM_frame = ttk.LabelFrame(second_col, text="Detectable Leak Rates (GPM)", padding="10")
        GPM_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        GPM_0 = ttk.Entry(GPM_frame, width=5)
        GPM_0.insert(0, 0.05)
        GPM_0.grid(row=0, column=0, sticky="w",padx=3)
        self.GPM_0 = GPM_0
        GPM_1 = ttk.Entry(GPM_frame, width=5)
        GPM_1.grid(row=0, column=1, sticky="w", padx=3)
        GPM_1.insert(0, 0.1)
        self.GPM_1 = GPM_1
        GPM_2 = ttk.Entry(GPM_frame, width=5)
        GPM_2.grid(row=0, column=2, sticky="w",padx=3)
        GPM_2.insert(0, 0.25)
        self.GPM_2 = GPM_2
        GPM_3 = ttk.Entry(GPM_frame, width=5)
        GPM_3.grid(row=0, column=3, sticky="w",padx=3)
        GPM_3.insert(0, 0.5)
        self.GPM_3 = GPM_3
        GPM_4 = ttk.Entry(GPM_frame, width=5)
        GPM_4.grid(row=0, column=4, sticky="w",padx=3)
        GPM_4.insert(0, 1.0)
        self.GPM_4 = GPM_4

        # Fracture Toughness
        fracture_frame = ttk.LabelFrame(second_col, text="Fracture Toughness", padding="10")
        fracture_frame.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(fracture_frame, text="Coef. C (-1/R):").grid(row=0, column=0, sticky="w")
        Coef_C_J_R = ttk.Entry(fracture_frame, width=10)
        Coef_C_J_R.insert(0, "1.5")
        Coef_C_J_R.grid(row=0, column=1, padx=5)
        self.Coef_C_J_R = Coef_C_J_R

        ttk.Label(fracture_frame, text="Exponent m:").grid(row=1, column=0, sticky="w")
        Exponent_m = ttk.Entry(fracture_frame, width=10)
        Exponent_m.insert(0, "0.43")
        Exponent_m.grid(row=1, column=1, padx=5)
        self.Exponent_m = Exponent_m

        ttk.Button(fracture_frame, text="Fit J-R Curve from Data", command=self.Fit_JRCurve_from_Data).grid(row=3, column=0, columnspan=2, pady=5)

        # ========== Section 4: Failure Criteria ==========
        failure_frame = ttk.LabelFrame(second_col, text="Failure Criteria", padding="10")
        failure_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        Failure_Criteria = tk.StringVar(value="Limit Load")
        ttk.Radiobutton(failure_frame, text="Limit Load", variable=Failure_Criteria, value="Limit Load").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(failure_frame, text="EPFM", variable=Failure_Criteria, value="EPFM").grid(row=0, column=1, sticky="w")
        self.Failure_Criteria = Failure_Criteria
        
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

    def Fit_ROCurve_from_Stress_Strain_Data(self):
        pass

    def Fit_ROCurve_from_YS_UTS(self):
        pass

    def Fit_JRCurve_from_Data(self):
        pass

    def new_analysis(self):
        #this is an code example code to show how to get value and set value.
        normal_pipe_size = self.Normal_Pipe_Size.get()
        print(normal_pipe_size)
        #how to clear the entry
        self.Normal_Pipe_Size.delete(0,tk.END)
        #how to set the value of entry
        self.Normal_Pipe_Size.insert(0,"123")
        
        pass

    def open_analysis(self):
        pass

    def save_analysis(self):
        pass

    def run_analysis(self):
        pass
    
    def run2_analysis(self):
        pass


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
