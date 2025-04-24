# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 14:39:27 2025

@author: arsalann
"""

import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.expressions import Beta, Variable
import biogeme.models as models

from biogeme.expressions import Beta, Variable


df = pd.read_excel('ExperimentLongDecoded_modified.xlsx')  # Assuming data is in a CSV file
database = db.Database('survey_db', df)


# Step 1: Identify the chosen alternative for each (RID, DESIGN_ROW) group
chosen_alternatives = df[df["choice"] == 1].groupby(["RID", "DESIGN_ROW"])["alternative"].first()

# Step 2: Map the chosen alternative back to all rows in the group
df["choice_biogeme"] = df.groupby(["RID", "DESIGN_ROW"])["alternative"].transform(
    lambda x: chosen_alternatives.get((x.name[0], x.name[1]))
)
df.to_excel("biogeme_ready.xlsx", index=False)

# Define variables (use the new choice column)
CHOICE = Variable('choice_biogeme')  # Critical change!
PLUG_IN_PAIRS = Variable('plug_in_pairs')
DAYS_PARTICIPATION = Variable('days_participation')
MIN_RANGE_KM = Variable('min_range_km')
REMUNERATION_SEK = Variable('remuneration_sek')

# Parameters (generic or alternative-specific)
BETA_PLUG_IN = Beta('BETA_PLUG_IN', 0, None, None, 0)
BETA_DAYS = Beta('BETA_DAYS', 0, None, None, 0)
BETA_RANGE = Beta('BETA_RANGE', 0, None, None, 0)
BETA_REMUNERATION = Beta('BETA_REMUNERATION', 0, None, None, 0)

# Utility functions with ASCs (optional)
ASC_1 = Beta('ASC_1', 0, None, None, 0)  # Alternative 1 constant
ASC_2 = Beta('ASC_2', 0, None, None, 0)  # Alternative 2 constant
# ASC_3 = 0 (normalized for opt-out)

V1 = ASC_1 + BETA_PLUG_IN * PLUG_IN_PAIRS + \
     BETA_DAYS * DAYS_PARTICIPATION + \
     BETA_RANGE * MIN_RANGE_KM + \
     BETA_REMUNERATION * REMUNERATION_SEK

V2 = ASC_2 + BETA_PLUG_IN * PLUG_IN_PAIRS + \
     BETA_DAYS * DAYS_PARTICIPATION + \
     BETA_RANGE * MIN_RANGE_KM + \
     BETA_REMUNERATION * REMUNERATION_SEK

V3 = 0  # Base alternative (opt-out)

# Map alternatives to utilities
V = {1: V1, 2: V2, 3: V3}
av = {1: 1, 2: 1, 3: 1}  # All alternatives available

# Estimate the model
logprob = models.loglogit(V, av, CHOICE)
biogeme = bio.BIOGEME(database, logprob)
results = biogeme.estimate()

# Print results
print(results.getEstimatedParameters())