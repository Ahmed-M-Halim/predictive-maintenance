from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


GOOGLE_API_KEY = 'AIzaSyAAKSTCzAMtrhn-N74wiqbqnZD9GJqlyu4'


RETRIVAL_DOC = {'machine_depreciation': "Indicators:\n•	High levels of wear metals: Fe, Pb, Cu, Sn, Cr, Al\n•	Fe > 30 ppm → gear wear\n•	Pb > 30 ppm → bearing overlay wear\n•	Cu/Sn > 20/10 ppm → bushing wear\n•	Cr/Al > 5–10 ppm → piston ring/liner damage\nCauses:\n•	Poor lubrication (oil degradation or wrong viscosity)\n•	Misalignment or overloading\n•	Extended oil drain intervals\n•	Contamination by hard particles or coolant\nSolutions:\n•	Reduce oil drain interval or use condition-based oil change\n•	Use higher-grade anti-wear or EP (extreme pressure) oil\n•	Inspect and replace worn components (bearings, bushings)\n•	Monitor wear rate over time to distinguish break-in vs. failure",
               'water_contamination': "Indicators:\n•	Water = Yes, Water > 0.1%\n•	Na > 50 ppm (from coolant)\n•	B < 3 ppm + Na > 30 ppm (coolant dilution)\n•	Rust formation, low dielectric strength\nCauses:\n•	Leaking gaskets or seals\n•	Faulty heat exchanger or cracked cylinder liner\n•	Condensation (cold starts, short runs)\n•	Coolant system leaks\nSolutions:\n•	Identify source via elemental analysis (Na, B, K)\n•	Pressure test cooling system\n•	Replace gaskets or seals\n•	Use water-separating filters or desiccant breathers",
               'dirt_in_oil': "Indicators:\n•	High Si (>10 ppm) + Al > 10 ppm\n•	Si > 5 ppm + B < 5 ppm (no boron additive support)\n•	Elevated Fe or Cr due to abrasive wear\nCauses:\n•	Defective or missing air filters\n•	Breathers not sealed properly\n•	Crankcase vacuum leak\n•	Operating in dusty environments\nSolutions:\n•	Replace/upgrade air filters (check for ISO 5011 spec)\n•	Install high-efficiency or dual-stage filtration\n•	Seal all intake systems\n•	Increase sampling frequency in dusty environments",
               'sludge_formation': "Indicators:\n•	OXI > 20 Abs/cm or TAN > 0.2\n•	Delta Viscosity (V40) > +15%\n•	TBN dropping while TAN rising\n•	Darkened or cloudy oil appearance\nCauses:\n•	High operating temperatures (>90–100°C)\n•	Long oil drain intervals\n•	Poor additive package (low oxidation inhibitors)\n•	Overloaded operation or poor cooling\nSolutions:\n•	Switch to higher oxidation-resistant oil (Group III or PAO)\n•	Install oil coolers or improve ventilation\n•	Reduce drain interval\n•	Use antioxidant additives (phenols, amines)",
               'oil_change_needed': "Indicators:\n•	TBN < 1.0 → no neutralizing reserve\n•	Delta viscosity > +10–15% (shearing or oxidation)\n•	Zn < 30 ppm, Ca < 100 ppm → detergent/additive depletion\n•	TAN > 0.18 → acid buildup\n•	Change in color, smell, or foam\nCauses:\n•	Long oil drain intervals\n•	High thermal or mechanical stress\n•	Contaminants degrading the additives\nSolutions:\n•	Change oil based on condition, not fixed time (use analytics)\n•	Switch to extended-drain synthetic oil with robust additive package",
               'normal': "Indicators:\n•	All wear metals within normal ranges\n•	TBN & TAN ratios are normal \n•	Stable viscosity\n•	No significant contaminants\n•	Additives present and not depleted\nMaintenance Strategy:\n•	Continue scheduled monitoring"}


class Reasoning_Model():
    
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["class", "sample", "reasoning"],
            template="""
            Role: You are a maintenance diagnostic assistant with expertise in interpreting oil analysis data to diagnose mechanical system conditions.
            Steps: Explain the reasoning of the diagnosis using the oil sample, by referencing its indicators. Suggest possible causes based on the sample. Recommend solutions based on the sample.

            Context: The oil analysis has been preliminarily diagnosed as {cls}. You are provided with a specific oil sample report: \n\n{sample}\n

            to evaluate this diagnosis. The objective is to show the reasoning for the diagnosis and support it using \n\n{reasoning}\n

            Format: Fill these sections: What led you to this decision?(header name = The Observation) (less than 30 words), What causes should I investigate?(header name = Investigation Points) (less than 30 words), What are the possible solutions based on your suggestion of the cause?(header name = The Solution) (less than 50 words), Paragrahp describtion to desribe every section combined as one. (less than 75 words)(header name = Story)
            """,
        )

        self.gemini = gemini = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )

        self.chain = LLMChain(
            llm=self.gemini,
            prompt=self.prompt,
            verbose=False
        )

    def generate_response(self, cls, sample):
        return self.chain.run(cls=cls, sample=sample, reasoning=RETRIVAL_DOC[cls])


# model = Reasoning_Model()
# print(model.generate_response('machine_depreciation', [5, 6, 0, 1, 3, 18, 1, 0, 8, 1, 44, 38, 2, 196, 0, 3.56, 12.83, 161.5, 9, 0.07, 11.5, 31, 1.2, 0, 0]))