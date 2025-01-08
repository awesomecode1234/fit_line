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
import json

class JRCurveFitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PREVENTURE")
        self.root.geometry("1080x720")
        self.root.configure(bg='lightgray')
        self.input_filename = ""
        self.output_filename = ""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Anaylysis", command=self.new_analysis)
        file_menu.add_command(label="Open Analysis", command=self.open_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Save Inputs", command=self.save_inputs)
        file_menu.add_command(label="Save Inputs As...", command=self.save_inputs_as)
        file_menu.add_command(label="Save Outputs", command=self.save_outputs)
        file_menu.add_command(label="Save Outputs as ...",command=self.save_outputs_as)
        file_menu.add_separator()
        # file_menu.add_command(label="Close Analysis")
        file_menu.add_command(label="Exit", command=self.exit_program)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.entryconfig("Save Outputs", state=tk.DISABLED)
        file_menu.entryconfig("Save Outputs as ...", state=tk.DISABLED)
        self.file_menu = file_menu

        batchrun_menu = tk.Menu(menubar, tearoff=0)
        batchrun_menu.add_command(label="Batch Run", command=self.batch_run)
        menubar.add_cascade(label="Batch Run", menu=batchrun_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About")
        menubar.add_cascade(label="About", menu=about_menu)

        root.config(menu=menubar)
        
        # Left Frame: Input Panel
        input_frame = ttk.Frame(root)
        input_frame.grid(row = 1, column =0, padx=10, pady=10)

        title_frame = tk.Frame(input_frame)
        title_frame.grid(row =1, column =0, rowspan=1, columnspan=2, sticky="nw",padx=10, pady=5)
        ttk.Label(title_frame, text="Analysis Title:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
        Analysis_Title = ttk.Entry(title_frame, width=30, justify=tk.RIGHT)
        Analysis_Title.insert(0, "Hot Leg SMAW")
        Analysis_Title.grid(row=0, column=1, padx=5, pady=2)
        self.Analysis_Title = Analysis_Title

        # Main Frame
        first_col = ttk.Frame(input_frame, width = 200)
        first_col.grid(row=2, column =0, padx=10, pady=10)

        toolbar_frame = tk.Frame(input_frame)
        toolbar_frame.grid(row =0, column =0, sticky="nw",padx=10, pady=5)
        
        new_image =   PhotoImage(file="new.png")
        open_image = PhotoImage(file="open.png")
        save_image = PhotoImage(file="save.png")
        run_image = PhotoImage(file="run2.png")
        
        new_button = Button(toolbar_frame, image=new_image, command=self.new_analysis)
        new_button.image = new_image
        new_button.pack(side=tk.LEFT)

        open_button = Button(toolbar_frame, image=open_image, command=self.open_analysis)
        open_button.image = open_image
        open_button.pack(side=tk.LEFT)

        save_button = Button(toolbar_frame, image=save_image, command=self.save_inputs)
        save_button.image = save_image
        save_button.pack(side=tk.LEFT)
        
        run_button = Button(toolbar_frame, image=run_image, command=self.run_analysis)
        run_button.image = run_image
        run_button.pack(side=tk.LEFT)

        

        pipe_frame = ttk.LabelFrame(first_col, text="Pipe & Loads", padding="10")
        pipe_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        ttk.Label(pipe_frame, text="Nominal Pipe Size (in)").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        Normal_Pipe_Size = ttk.Entry(pipe_frame, width=10, justify=tk.RIGHT)
        Normal_Pipe_Size.insert(0, 12)
        Normal_Pipe_Size.grid(row=0, column=1, padx=5, pady=2)
        self.Normal_Pipe_Size = Normal_Pipe_Size

        ttk.Label(pipe_frame, text="Pipe OD (in)").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        Pipe_OD = ttk.Entry(pipe_frame, width=10, justify=tk.RIGHT)
        Pipe_OD.insert(0, 12)
        Pipe_OD.grid(row=1, column=1, padx=5, pady=2)
        self.Pipe_OD = Pipe_OD

        ttk.Label(pipe_frame, text="Wall Thickness (in)").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        Wall_Thickness = ttk.Entry(pipe_frame, width=10, justify=tk.RIGHT)
        Wall_Thickness.insert(0, 0.5)
        Wall_Thickness.grid(row=2, column=1, padx=5, pady=2)
        self.Wall_Thickness = Wall_Thickness

        ttk.Label(pipe_frame, text="Pressure (psi)").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        Pressure = ttk.Entry(pipe_frame, width=10, justify=tk.RIGHT)
        Pressure.insert(0, 2250)
        Pressure.grid(row=3, column=1, padx=5, pady=2)
        self.Pressure = Pressure

        ttk.Label(pipe_frame, text="Temperature (°F)").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        Temperature = ttk.Entry(pipe_frame, width=10, justify=tk.RIGHT)
        Temperature.insert(0, 600)
        Temperature.grid(row=4, column=1, padx=5, pady=2)
        self.Temperature = Temperature

        # BAC section
        bac_frame = ttk.LabelFrame(first_col, text="BAC", padding="10")
        bac_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        ttk.Label(bac_frame, text="Max. Op. Stress (ksi)").grid(row=0, column=0, sticky="w", padx=5)
        Max_Op_Stress = ttk.Entry(bac_frame, width=10, justify=tk.RIGHT)
        Max_Op_Stress.insert(0, "55")
        Max_Op_Stress.grid(row=0, column=1)
        self.Max_Op_Stress = Max_Op_Stress

        ttk.Label(bac_frame, text="No. of Points").grid(row=1, column=0, sticky="w", padx=5)
        No_Of_Points = ttk.Entry(bac_frame, width=10, justify=tk.RIGHT)
        No_Of_Points.insert(0, "15")
        No_Of_Points.grid(row=1, column=1)
        self.No_Of_Points = No_Of_Points

        # Radio Buttons
        Pts_dist = tk.StringVar(value="BIASED")
        ttk.Radiobutton(bac_frame, text="Equidistant", variable=Pts_dist, value="EQUIDISTANT").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(bac_frame, text="Biased", variable=Pts_dist, value="BIASED").grid(row=2, column=1, sticky="w")
        self.Pts_dist = Pts_dist

        Materials = ["1. ASME SA-312 BM/TIG", "2. ASME SA-312, 304 Weld", "3. ASME SA-312, 304L Weld", "4. ASME SA-106 Gr B (Base Metal)", 
        "5. ASME SA-106 Gr C (Base Metal)", "6. ASME SA-335. Gr P11 (Base Metal)", "7. ASME SA-106 Gr B (Weld Metal)", "8. ASME SA-106 Gr C (Weld Metal)", "9. ASME SA-335. Gr P11 (Weld Metal)",
        "10. Limit Load", "11. Austenitic C-6330", "12. Ferritic C-6331-1 Cat 1", "13. Ferritic C-6331-1 Cat 2", "14. EPFM (J-Based)"]
        
        self.Materials = Materials
        TypeOption= tk.StringVar(root)
        TypeOption.set(Materials[2])  # default value
        optionmenu = tk.OptionMenu(first_col, TypeOption, *Materials)
        optionmenu.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        TypeOption.trace("w", self.update_material)
        self.TypeOption = TypeOption
        
        tensile_frame = ttk.LabelFrame(first_col, text="Tensile Properties", padding="10")

        tensile_frame.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        
        ttk.Label(tensile_frame, text="Yield Strength (ksi)").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        Yield_Strength = ttk.Entry(tensile_frame, width=10, justify=tk.RIGHT)
        Yield_Strength.insert(0, "30")
        Yield_Strength.grid(row=0, column=1, padx=5, pady=2)
        self.Yield_Strength = Yield_Strength

        ttk.Label(tensile_frame, text="UTS (ksi)").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        UTS = ttk.Entry(tensile_frame, width=10, justify=tk.RIGHT)
        UTS.insert(0, "60")
        UTS.grid(row=1, column=1, padx=5, pady=2)
        self.UTS = UTS

        ttk.Label(tensile_frame, text="Elastic Modulus (ksi)").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        Elastic_Modulus = ttk.Entry(tensile_frame, width=10, justify=tk.RIGHT)
        Elastic_Modulus.insert(0, "28000")
        Elastic_Modulus.grid(row=2, column=1, padx=5, pady=2)
        self.Elastic_Modulus = Elastic_Modulus

        ttk.Label(tensile_frame, text="RO Alpha").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        RO_Alpha = ttk.Entry(tensile_frame, width=10, justify=tk.RIGHT)
        RO_Alpha.insert(0, "4.5")
        RO_Alpha.grid(row=3, column=1, padx=5, pady=2)
        self.RO_Alpha = RO_Alpha

        ttk.Label(tensile_frame, text="RO n").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        RO_n = ttk.Entry(tensile_frame, width=10, justify=tk.RIGHT)
        RO_n.insert(0, "3.5")
        RO_n.grid(row=4, column=1, padx=5, pady=2)
        self.RO_n = RO_n

        # Buttons
        Fit_RO_Curve_from_Data =ttk.Button(first_col, text="Fit R-O Curve from Stress-Strain Data", command=self.Fit_ROCurve_from_Stress_Strain_Data)
        Fit_RO_Curve_from_Data.grid(row=4, column=0, pady=5)
        self.Fit_RO_Curve_from_Data = Fit_RO_Curve_from_Data
        Fit_RO_Curve_from_YS_UTS =ttk.Button(first_col, text="      Fit R-O Curve from YS-UTS      ", command=self.Fit_ROCurve_from_YS_UTS)
        Fit_RO_Curve_from_YS_UTS.grid(row=5, column=0, pady=5)
        self.Fit_RO_Curve_from_YS_UTS = Fit_RO_Curve_from_YS_UTS
        # ========== Section 3: Crack Morphology ==========
        second_col = ttk.Frame(input_frame)
        second_col.grid(row=2, column=1, sticky="nw", padx=10, pady=10)
        crack_frame = ttk.LabelFrame(second_col, text="Crack Morphology", padding="10")
        crack_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        CrackMorphology = tk.StringVar(value="FATIGUE")
        ttk.Radiobutton(crack_frame, text="IGSCC", variable=CrackMorphology, value="IGSCC").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Radiobutton(crack_frame, text="PWSCC Weld", variable=CrackMorphology, value="PWSCCW").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Radiobutton(crack_frame, text="User-Defined", variable=CrackMorphology, value="USERDEF").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Radiobutton(crack_frame, text="Cor. Fatigue", variable=CrackMorphology, value="CFATIGUE").grid(row=0, column=1, sticky="w", pady=2)
        ttk.Radiobutton(crack_frame, text="Fatigue", variable=CrackMorphology, value="FATIGUE").grid(row=1, column=1, sticky="w", pady=2)
        ttk.Radiobutton(crack_frame, text="PWSCC BM", variable=CrackMorphology, value="PWSCCBM").grid(row=2, column=1, sticky="w", pady=2)
    
        CrackMorphology.trace("w", self.update_crack_morphology)
        self.CrackMorphology = CrackMorphology
    
        ttk.Label(crack_frame, text="45 Degree Turns").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        Degree_Turns = ttk.Entry(crack_frame, width=10, justify=tk.RIGHT)
        Degree_Turns.grid(row=3, column=1, padx=5, pady=2)
        self.Degree_Turns = Degree_Turns

        ttk.Label(crack_frame, text="Roughness").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        Roughness = ttk.Entry(crack_frame, width=10, justify=tk.RIGHT)
        Roughness.grid(row=4, column=1, padx=5, pady=2)
        self.Roughness = Roughness

        

        GPM_frame = ttk.LabelFrame(second_col, text="Detectable Leak Rates (GPM)", padding="10")
        GPM_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        GPM_0 = ttk.Entry(GPM_frame, width=5, justify=tk.RIGHT)
        GPM_0.insert(0, 0.05)
        GPM_0.grid(row=0, column=0, sticky="w",padx=3)
        self.GPM_0 = GPM_0
        GPM_1 = ttk.Entry(GPM_frame, width=5, justify=tk.RIGHT)
        GPM_1.grid(row=0, column=1, sticky="w", padx=3)
        GPM_1.insert(0, 0.1)
        self.GPM_1 = GPM_1
        GPM_2 = ttk.Entry(GPM_frame, width=5, justify=tk.RIGHT)
        GPM_2.grid(row=0, column=2, sticky="w",padx=3)
        GPM_2.insert(0, 0.25)
        self.GPM_2 = GPM_2
        GPM_3 = ttk.Entry(GPM_frame, width=5, justify=tk.RIGHT)
        GPM_3.grid(row=0, column=3, sticky="w",padx=3)
        GPM_3.insert(0, 0.5)
        self.GPM_3 = GPM_3
        GPM_4 = ttk.Entry(GPM_frame, width=5, justify=tk.RIGHT)
        GPM_4.grid(row=0, column=4, sticky="w",padx=3)
        GPM_4.insert(0, 1.0)
        self.GPM_4 = GPM_4

        # Fracture Toughness
        fracture_frame = ttk.LabelFrame(second_col, text="Fracture Toughness", padding="10")
        fracture_frame.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(fracture_frame, text="Coef. C (-1/R):").grid(row=0, column=0, sticky="w")
        Coef_C_J_R = ttk.Entry(fracture_frame, width=10,justify=tk.RIGHT)
        Coef_C_J_R.insert(0, "1.5")
        Coef_C_J_R.grid(row=0, column=1, padx=5)
        self.Coef_C_J_R = Coef_C_J_R

        ttk.Label(fracture_frame, text="Exponent m:").grid(row=1, column=0, sticky="w")
        Exponent_m = ttk.Entry(fracture_frame, width=10, justify=tk.RIGHT)
        Exponent_m.insert(0, "0.43")
        Exponent_m.grid(row=1, column=1, padx=5)
        self.Exponent_m = Exponent_m

        Fit_JRCurve_from_Data_btn = ttk.Button(fracture_frame, text="Fit J-R Curve from Data", command=self.Fit_JRCurve_from_Data)
        Fit_JRCurve_from_Data_btn.grid(row=3, column=0, columnspan=2, pady=5)
        self.Fit_JRCurve_from_Data_btn = Fit_JRCurve_from_Data_btn
        Calculate_btn = ttk.Button(second_col, text="Calculate", command=self.Calculate)
        Calculate_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        # ========== Section 5: Output ==========
        # Table Frame
        table_frame = ttk.Frame(input_frame)
        table_frame.grid(row=2, column=2, padx=10, pady=10)

        # Plot Frame
        plot_frame = ttk.Frame(input_frame, width =300)
        plot_frame.grid(row=2, column =2, padx=10, pady=10)

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
        self.update_material()
        self.update_crack_morphology()

    def load_data(self):
        with open(self.input_filename, "r") as file:
            json_data = json.load(file)  
        self.json_data = json_data
        self.new_analysis()
        self.Analysis_Title.insert(0, json_data["analysis_title"])
        self.Normal_Pipe_Size.insert(0, json_data["nps"])
        self.Pipe_OD.insert(0, json_data["od"])
        self.Wall_Thickness.insert(0, json_data["pipet"])
        self.Pressure.insert(0, json_data["pr_ksi"])
        self.Temperature.insert(0, json_data["temp_f"])
        self.Max_Op_Stress.insert(0, json_data["max_op_stress"])
        self.No_Of_Points.insert(0, json_data["num_points"])
        self.Pts_dist.set(json_data["pts_dist"])
        # self.TypeOption.set(json_data["material"])
        self.GPM_0.insert(0, json_data["leak_rates"][0])
        self.GPM_1.insert(0, json_data["leak_rates"][1])
        self.GPM_2.insert(0, json_data["leak_rates"][2])
        self.GPM_3.insert(0, json_data["leak_rates"][3])
        self.GPM_4.insert(0, json_data["leak_rates"][4])
        self.CrackMorphology.set("USERDEF")
        self.Degree_Turns.insert(0, json_data["n90turns"])
        self.Roughness.insert(0, json_data["roughness"])
        self.TypeOption.set(self.Materials[13])
        self.Yield_Strength.insert(0, json_data["yield_strength"])
        self.UTS.insert(0, json_data["uts"])
        self.Elastic_Modulus.insert(0, json_data["elas_mod"])
        self.RO_Alpha.insert(0, json_data["ro_alpha"])
        self.RO_n.insert(0, json_data["ro_n"])
        self.Coef_C_J_R.insert(0, json_data["c_jr"])
        self.Exponent_m.insert(0, json_data["m_jr"])
        self.TypeOption.set(self.Materials[json_data["material"]-1])
        self.CrackMorphology.set(json_data["morph"])
    def save_data(self):
        json_data = {}
        json_data['analysis_title'] = self.Analysis_Title.get()
        json_data['nps'] = self.Normal_Pipe_Size.get()
        json_data['od'] = self.Pipe_OD.get()
        json_data['pipet'] = self.Wall_Thickness.get()
        json_data['pr_ksi'] = self.Pressure.get()
        json_data['temp_f'] = self.Temperature.get()
        json_data['max_op_stress'] = self.Max_Op_Stress.get()
        json_data['num_points'] = self.No_Of_Points.get()
        json_data['pts_dist'] = self.Pts_dist.get()
        json_data['leak_rates'] = [self.GPM_0.get(), self.GPM_1.get(), self.GPM_2.get(), self.GPM_3.get(), self.GPM_4.get()]
        json_data['morph'] = self.CrackMorphology.get()
        json_data['n90turns'] = self.Degree_Turns.get()
        json_data['roughness'] = self.Roughness.get()
        json_data['yield_strength'] = self.Yield_Strength.get()
        json_data['uts'] = self.UTS.get()
        json_data['elas_mod'] = self.Elastic_Modulus.get()
        json_data['ro_alpha'] = self.RO_Alpha.get()
        json_data['ro_n'] = self.RO_n.get()
        json_data['c_jr'] = self.Coef_C_J_R.get()
        json_data['m_jr'] = self.Exponent_m.get()
        json_data['material'] = self.Materials.index(self.TypeOption.get())+1
        self.json_data = json_data
        with open(self.input_filename, 'w') as file:
            json.dump(json_data, file, indent=4)

    def Fit_ROCurve_from_Stress_Strain_Data(self):
        self.import_data()
        self.fit_curve()
        self.RO_Alpha.delete(0, tk.END)
        self.RO_n.delete(0, tk.END)
        self.RO_Alpha.insert(0, f"{self.fit_params[0]:.2f}")
        self.RO_n.insert(0, f"{self.fit_params[1]:.2f}")
        pass

    def Fit_ROCurve_from_YS_UTS(self):
        pass


    def Fit_JRCurve_from_Data(self):
        self.import_data()
        self.fit_curve()
        self.Coef_C_J_R.delete(0, tk.END)
        self.Exponent_m.delete(0, tk.END)
        self.Coef_C_J_R.insert(0, f"{self.fit_params[0]:.2f}")
        self.Exponent_m.insert(0, f"{self.fit_params[1]:.2f}")
        pass

    def Calculate(self):
        self.file_menu.entryconfig("Save Outputs", state=tk.NORMAL)
        self.file_menu.entryconfig("Save Outputs as ...", state=tk.NORMAL)
        pass
    
    def update_material(self, *args):
        material_index = self.Materials.index(self.TypeOption.get()) + 1
        if material_index <= 9:
            newState = tk.DISABLED
        else:
            newState = tk.NORMAL
        
        if material_index == 13:
            self.Coef_C_J_R.config(state = tk.NORMAL)
            self.Exponent_m.config(state = tk.NORMAL)
            self.Fit_JRCurve_from_Data_btn.config(state = tk.NORMAL)
        else:
            self.Coef_C_J_R.config(state = tk.DISABLED)
            self.Exponent_m.config(state = tk.DISABLED)
            self.Fit_JRCurve_from_Data_btn.config(state = tk.DISABLED)
        self.Yield_Strength.config(state = newState)
        self.UTS.config(state = newState)
        self.Elastic_Modulus.config(state = newState)
        self.RO_Alpha.config(state = newState)
        self.RO_n.config(state = newState)
        self.Fit_RO_Curve_from_Data.config(state = newState)
        self.Fit_RO_Curve_from_YS_UTS.config(state = newState)

    def update_crack_morphology(self, *args):
        if self.CrackMorphology.get() == "USERDEF":
            self.Degree_Turns.config(state = tk.NORMAL)
            self.Roughness.config(state = tk.NORMAL)
        else:
            self.Degree_Turns.config(state = tk.DISABLED)
            self.Roughness.config(state = tk.DISABLED)

    def new_analysis(self):
        
        self.Analysis_Title.delete(0, tk.END)
        self.Normal_Pipe_Size.delete(0, tk.END)
        self.Pipe_OD.delete(0, tk.END)
        self.Wall_Thickness.delete(0, tk.END)
        self.Pressure.delete(0, tk.END)
        self.Temperature.delete(0, tk.END)
        self.Max_Op_Stress.delete(0, tk.END)
        self.No_Of_Points.delete(0, tk.END)
        self.GPM_0.delete(0, tk.END)
        self.GPM_1.delete(0, tk.END)
        self.GPM_2.delete(0, tk.END)
        self.GPM_3.delete(0, tk.END)
        self.GPM_4.delete(0, tk.END)
        self.Degree_Turns.delete(0, tk.END)
        self.Roughness.delete(0, tk.END)
        self.Yield_Strength.delete(0, tk.END)
        self.UTS.delete(0, tk.END)
        self.Elastic_Modulus.delete(0, tk.END)
        self.RO_Alpha.delete(0, tk.END)
        self.RO_n.delete(0, tk.END)
        self.Coef_C_J_R.delete(0, tk.END)
        self.Exponent_m.delete(0, tk.END)
        self.update_material()
        self.update_crack_morphology()
        
    def open_analysis(self):
        input_filename = filedialog.askopenfilename(title="Select JSON file", filetypes=[("JSON files", "*.json, *.jsn")])
        if input_filename:
            self.input_filename = input_filename
            self.load_data()
        pass
    
    def save_inputs(self):
        if self.input_filename == "":
            input_filename = filedialog.asksaveasfilename(title="Save into JSON file", filetypes=[("JSON files", "*.json, *.jsn")])
            if input_filename:
                self.input_filename = input_filename
            else:
                return False
        self.save_data()
        return True

    def save_inputs_as(self):
        input_filename = filedialog.asksaveasfilename(title="Save as new JSON file", filetypes=[("JSON files", "*.json, *.jsn")])
        if input_filename:
            self.input_filename = input_filename
        else:
            return
        self.save_data()

    def save_outputs(self):
        if self.output_filename == "":
            output_filename = filedialog.asksaveasfilename(title="Save into PDF file", filetypes=[("PDF files", "*.pdf")])
            if output_filename:
                self.output_filename = output_filename
            else:
                return False
        
        self.generate_report()
        return True
    
    def save_outputs_as(self):
        pass

    def exit_program(self):
        response = messagebox.askyesno("Warning", "Inputs and Outputs will be lost. Are you sure you want to exit without saving?")
        if response:
            self.root.destroy()
        else:
            is_saved = self.save_inputs()
            if not is_saved:
                return
            is_saved = self.save_outputs()
            if not is_saved:
                return
            self.root.destroy()

    def run_analysis(self):
        pass
    
    def batch_run(self):
        dialog = BatchRunDialog(self.root)
        if dialog.result:
            print("Files Selected:", dialog.result)  # Data passed back from the modal

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

class BatchRunDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.file_list = []
        self.result = None  # To store the selected files
        self.setup_ui()

        # Make modal
        self.grab_set()
        self.transient(parent)
        self.wait_window(self)

    def setup_ui(self):
        self.title("Ramberg-Osgood Fit")
        self.geometry("1080x700")
        
        # Listbox to display files
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(button_frame, text="Add Files", width=20, command=self.add_files).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        tk.Button(button_frame, text="Remove Selected Files", width=20, command=self.remove_files).grid(row=1, column=0, padx=20, pady=10, sticky="W")
        tk.Button(button_frame, text="Run the Files", width=20, command=self.run_files).grid(row=0, column=1, padx=20, pady=10, sticky="E")
        tk.Button(button_frame, text="Close", width=20, command=self.close).grid(row=1, column=1, padx=20, pady=10, sticky="E")

        # Footer label
        self.footer_label = tk.Label(self, text="0 Files Added", anchor="w")
        self.footer_label.pack(fill=tk.X, padx=5, pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select Files", filetypes=[("JSON Files", "*.json, *.JSON, *.jsn"), ("All Files", "*.*")])
        if files:
            self.file_list.extend(files)
            self.update_listbox()
            
    def remove_files(self):
        selected_indices = self.listbox.curselection()
        for index in reversed(selected_indices):
            del self.file_list[index]
        self.update_listbox()

    def run_files(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "No files to run!")
        else:
            self.result = self.file_list  # Save the list of files for main window
            self.close()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in self.file_list:
            self.listbox.insert(tk.END, file)
        self.footer_label.config(text=f"{len(self.file_list)} Files Added")

    def close(self):
        self.destroy()  # Close the dialog



if __name__ == "__main__":
    root = tk.Tk()
    app = JRCurveFitApp(root)
    root.mainloop()
