import json
from datetime import datetime
from enum import Enum
from typing import List
from jsonschema import validate, ValidationError as SchemaValidationError
from pydantic import BaseModel, Field, ValidationError, constr, model_validator
# import globals


# Define enums
class Mode(str, Enum):
	LL = "LL"
	EPFM = "EPFM"


class Points(str, Enum):
	BIASED = "BIASED"
	EQD = "EQD"


class Morph(str, Enum):
	FATIGUE = "FATIGUE"
	PWSCCW = "PWSCCW"
	PWSCCBM = "PWSCCBM"
	CFATIGUE = "CFATIGUE"
	IGSCC = "IGSCC"
	USERDEF = "USERDEF"


# Define the Inputs class as a Pydantic model
class Inputs(BaseModel):
	input_ver: constr(max_length=20)
	analysis_title: constr(max_length=100)
	nps: int = Field(..., ge=1, lt=100)  # >=1 and <100
	od: float = Field(..., gt=0.0)  # >0.0
	pipet: float = Field(..., gt=0.0)  # >0.0
	pr_ksi: float = Field(..., gt=0.0)  # >0.0
	temp_f: float = Field(..., gt=0.0)  # >0.0
	max_op_stress: float = Field(..., gt=0.0)  # >0.0
	num_points: int = Field(..., ge=5)  # >=5
	pts_dist: Points
	leak_rates: List[float] = Field(..., max_items=5, min_items=1)  # Max 5 values
	morph: Morph
	n90turns: int = Field(..., ge=1)  # >=1
	roughness: float = Field(..., gt=0.0)  # >0.0
	mode: Mode
	material: int
	yield_strength: float = Field(..., gt=0.0)  # >0.0
	uts: float = Field(..., gt=0.0)  # >0.0
	elas_mod: float = Field(..., gt=0.0)  # >0.0
	ro_alpha: float = Field(..., gt=0.0)  # >0.0
	ro_n: float = Field(..., gt=0.0)  # >0.0
	c_jr: float = Field(..., gt=0.0)  # >0.0
	m_jr: float = Field(..., gt=0.0)  # >0.0

	# Custom validation for leak_rates and Rm/t condition
	@model_validator(mode="before")
	def validate(cls, values):
		"""

		:param values:
		:return:
		"""
		return values
		# Ensure all leak_rates > 0
		leak_rates = values.get("leak_rates", [])
		if any(rate <= 0 for rate in leak_rates):
			raise ValueError("All values in 'leak_rates' must be greater than 0.")

		# Check the Rm/t condition: 0.5 * (od - pipet) >= 2
		od = values.get("od", 0)
		pipet = values.get("pipet", 0)
		rm_t = 0.5 * (od - pipet)
		if rm_t < 2:
			raise ValueError(f"Rm/t (calculated as 0.5 * (od - pipet)) must be >= 2. Current value: {rm_t:.2f}")
		return values

	# Generate schema from Inputs class
	# schema = Inputs.model_json_schema()

	# Save schema to a file (optional)
	# with open("Inputs.schema", "w") as schema_file:
	#	json.dump(schema, schema_file, indent=4)

	# Validate JSON file against schema
	@staticmethod
	def validate_inputs(json_file_path):
		schema = Inputs.model_json_schema()
		with open(json_file_path, "r") as json_file:
			json_data = json.load(json_file)

		try:
			# Validate JSON against schema
			validate(instance=json_data, schema=schema)
			print("The structure of the input file is correct.")

			# Deserialize JSON to Inputs instance
			inputs_instance = Inputs(**json_data)
		# print("\nDeserialized Inputs Instance:")
		# print(inputs_instance)
		# return inputs_instance
		except SchemaValidationError as ex:
			print(f"Validation Error in field '{'.'.join(ex.path)}': {ex.message}")
		except ValidationError as ve:
			print("Other Errors:")
			for error in ve.errors():
				loc = error.get("loc", [])
				field = loc[0] if loc else "Unknown"
				message = error.get("msg", "Validation error")
				print(f"Field '{field}': {message}")
		else:
			inputs_instance = Inputs(**json_data)
			self = inputs_instance
			return self

	def write_report(self, file_out):
		"""

		:param file_out:
		:return:
		"""
		dt = datetime.now()
		globals.rpt_str.clear()
		globals.rpt_str.append(globals.app_name + "  Version: " + globals.app_ver)
		globals.rpt_str.append("Developer: " + globals.app_dev)
		globals.rpt_str.append(dt.strftime("%B %d, %Y   %H:%M:%S"))
		globals.rpt_str.append("Analysis Title: " + self.analysis_title)
		globals.rpt_str.append("Pipe Dimensions and Operating Conditions")
		globals.rpt_str.append('   NPS = {:2.0f}'.format(self.nps))
		globals.rpt_str.append('   Pipe Outside Diameter (in) = {:0.3f}'.format(self.od))
		globals.rpt_str.append('   Pipe Wall Thickness (in) = {:0.3f}'.format(self.pipet))
		globals.rpt_str.append('   Pressure (ksi) = {:0.4f}'.format(self.pr_ksi))
		globals.rpt_str.append('   Temperature (deg F) = {:0.2f}'.format(self.temp_f))
		globals.rpt_str.append('   Max. Operating Stress = {:0.2f}'.format(self.max_op_stress))
		globals.rpt_str.append('   No. of Points = {:0.0f}'.format(self.num_points))
		globals.rpt_str.append('   Points Bias = {}'.format(self.pts_dist))
		globals.rpt_str.append("Leak Rates and Crack Morphology")
		globals.rpt_str.append('   Leak Rates (gpm) =')
		for lr in self.leak_rates:
			globals.rpt_str.append('                 {}'.format(lr))
		globals.rpt_str.append('   Morphology = {}'.format(self.morph))
		globals.rpt_str.append('   90 Degree Turns = {:0.0f}'.format(self.n90turns))
		globals.rpt_str.append('   roughness (in) = {:0.6f}'.format(self.roughness))
		globals.rpt_str.append("Failure Mode and Material Properties")
		globals.rpt_str.append('   Failure Mode = {}'.format(self.mode))
		globals.rpt_str.append('   Material = {:0.0f}'.format(self.material))
		globals.rpt_str.append('   Yield Strength (ksi) = {:0.2f}'.format(self.yield_strength))
		globals.rpt_str.append('   UTS (ksi) = {:0.2f}'.format(self.uts))
		globals.rpt_str.append('   Elastic Modulus (ksi) = {:0.1f}'.format(self.elas_mod))
		globals.rpt_str.append('   R-O alpah = {:0.2f}'.format(self.ro_alpha))
		globals.rpt_str.append('   R-O n = {:0.2f}'.format(self.ro_n))
		globals.rpt_str.append('   C J-R (in-kips/in^2 = {:0.4f}'.format(self.c_jr))
		globals.rpt_str.append('   m J-R = {:0.4f}'.format(self.m_jr))


# end of class Inputs
# Validate input file
# current_dir = Path(__file__).parent
# file_in = globals.test_fldr + "HLSMAW.jsn"
# ins = Inputs.validate_inputs(file_in)
# if ins is not None:
#	print(ins.morph)
#	ins.write_report()
