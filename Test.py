Build a data processing and estimation engine (Excel VBA or Python) for monthly utility data across multiple countries and facilities.

The system processes two categories of data:

1. Energy (Electricity, Natural Gas, District Heating, District Cooling)
2. Water

Each record contains:

* Country
* Facility
* Month
* Source
* Usage (Actual, Estimated, or Both)
* Cost (Actual or Estimated)

Core rules:

1. Energy Usage Logic:

* If only Actual exists → use Actual
* If only Estimated exists → use Estimated
* If both exist → use (Actual + Estimated) and mark as Estimated

2. Energy Cost Logic:

* Cost is mandatory
* If cost is missing → estimate it
* Cost estimation must happen even if usage is estimated

3. Water Usage Logic:

* If Actual exists → use Actual
* If missing → must estimate (no fallback)

4. Dynamic Estimation Month:

* User provides an InputMonth (e.g., March = 3)
* Identify EnergyMaxMonth (latest month with energy data)
* EstimationMonth = MIN(InputMonth, EnergyMaxMonth)
* All estimations (especially water) should only be performed up to EstimationMonth

5. Estimation Inputs:

* Previous year same month data
* Headcount
* Average presence
* Floor area
* Country-specific rules

6. Estimation Approaches (multiple methods must be supported):

* Previous year same month
* Headcount scaling
* Presence scaling
* Floor area scaling
* Reference facility scaling

Reference facility estimation:
Estimated Value (Target Facility) =
Reference Facility Usage
× (Target Headcount / Reference Headcount)
× (Target Presence / Reference Presence)
× (Target Floor Area / Reference Floor Area)

7. Multi-Method Comparison Framework:

* Generate estimates using multiple methods (Est_A, Est_B, Est_C, etc.)
* If Actual data is available:
  → Calculate error = ABS(Actual - Estimate)
  → Select method with lowest error
* If Actual is not available:
  → Use historical performance (past error rates) to choose best method
* If no history exists:
  → Apply rule-based selection (country/facility/source)

8. Optional Enhancement:

* Use weighted average of multiple estimation methods based on historical accuracy

9. Edge Cases:

* No energy data available → estimation should default to InputMonth
* Missing previous year data → fallback to averages or alternative logic
* Division by zero (headcount, presence, etc.) must be handled safely

10. System Design Recommendation:

* Separate modules/functions:

  * GetEnergyMaxMonth
  * GetEstimationMonth
  * EstimateEnergy
  * EstimateWater
  * EstimateFromReference
  * CompareEstimationMethods
* Maintain lookup tables for:

  * Country-specific estimation rules
  * Historical performance of methods
  * Previous year data

The system should act as a rule-based estimation engine capable of:

* Handling missing data intelligently
* Applying multiple estimation strategies
* Comparing and selecting optimal methods dynamically
* Scaling across countries and facilities

The final output should include:

* Final Usage
* Final Cost
* Final Type (Actual / Estimated)
* Selected Estimation Method (if applicable)
