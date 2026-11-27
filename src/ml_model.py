import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from validation import validate_dol_configuration


class DOLRecommendationModel:

    def __init__(self):

        self.dataset = None

        # Separate Random Forest models
        self.protection_model = None
        self.contactor_model = None
        self.overload_model = None

        self.feature_columns = [
            "Motor_Power_kW",
            "Motor_Current_A"
        ]

    # ============================================================
    # LOAD DATASET
    # ============================================================

    def load_dataset(self):

        print("\nLoading IntelliPanel master dataset...")

        self.dataset = pd.read_csv(
            "data/intellipanel_master_dataset.csv"
        )

        print(
            "Dataset rows:",
            len(self.dataset)
        )

        print(
            "Dataset columns:",
            len(self.dataset.columns)
        )

    # ============================================================
    # TRAIN RANDOM FOREST MODELS
    # ============================================================

    def train(self):

        print("\nTraining Random Forest models...")

        # ========================================================
        # PROTECTION MODEL
        # ========================================================

        protection_data = self.dataset[
            self.feature_columns
            + ["Protection_Model"]
        ].dropna()

        if len(protection_data) > 0:

            self.protection_model = RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42
            )

            self.protection_model.fit(
                protection_data[
                    self.feature_columns
                ],
                protection_data[
                    "Protection_Model"
                ]
            )

        # ========================================================
        # CONTACTOR MODEL
        # ========================================================

        contactor_data = self.dataset[
            self.feature_columns
            + ["Contactor_Model"]
        ].dropna()

        if len(contactor_data) > 0:

            self.contactor_model = RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42
            )

            self.contactor_model.fit(
                contactor_data[
                    self.feature_columns
                ],
                contactor_data[
                    "Contactor_Model"
                ]
            )

        # ========================================================
        # OVERLOAD MODEL
        # ========================================================

        overload_data = self.dataset[
            self.feature_columns
            + ["Overload_Model"]
        ].dropna()

        if len(overload_data) > 0:

            self.overload_model = RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42
            )

            self.overload_model.fit(
                overload_data[
                    self.feature_columns
                ],
                overload_data[
                    "Overload_Model"
                ]
            )

        print(
            "Random Forest models trained successfully!"
        )

        print(
            "Protection model training rows:",
            len(protection_data)
        )

        print(
            "Contactor model training rows:",
            len(contactor_data)
        )

        print(
            "Overload model training rows:",
            len(overload_data)
        )

    # ============================================================
    # NORMALIZE TEXT
    # ============================================================

    @staticmethod
    def normalize_text(value):

        if pd.isna(value):
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )

    # ============================================================
    # VOLTAGE MATCHING
    # ============================================================

    @staticmethod
    def voltage_matches(
        value,
        requested_voltage
    ):

        if pd.isna(value):
            return False

        text = str(value).strip()

        if "/" in text:

            parts = text.split("/")

            for part in parts:

                try:

                    if (
                        float(part.strip())
                        ==
                        float(requested_voltage)
                    ):
                        return True

                except ValueError:

                    continue

            return False

        try:

            return (
                float(text)
                ==
                float(requested_voltage)
            )

        except ValueError:

            return False

    # ============================================================
    # COORDINATION MATCHING
    # ============================================================

    @staticmethod
    def coordination_matches(
        value,
        requested_coordination
    ):

        if pd.isna(value):
            return False

        configuration = (
            str(value)
            .strip()
            .lower()
            .replace("iec", "")
            .strip()
        )

        requested = (
            str(requested_coordination)
            .strip()
            .lower()
            .replace("iec", "")
            .strip()
        )

        return (
            configuration
            ==
            requested
        )

    # ============================================================
    # PREDICT COMPONENT PROBABILITIES
    # ============================================================

    def get_component_probabilities(
        self,
        motor_power_kw,
        motor_current_a
    ):

        prediction_input = pd.DataFrame(
            [[
                motor_power_kw,
                motor_current_a
            ]],
            columns=self.feature_columns
        )

        probabilities = {}

        # --------------------------------------------------------
        # PROTECTION
        # --------------------------------------------------------

        if self.protection_model is not None:

            probability_array = (
                self.protection_model
                .predict_proba(
                    prediction_input
                )[0]
            )

            classes = (
                self.protection_model
                .classes_
            )

            probabilities["Protection_Model"] = dict(
                zip(
                    classes,
                    probability_array
                )
            )

        # --------------------------------------------------------
        # CONTACTOR
        # --------------------------------------------------------

        if self.contactor_model is not None:

            probability_array = (
                self.contactor_model
                .predict_proba(
                    prediction_input
                )[0]
            )

            classes = (
                self.contactor_model
                .classes_
            )

            probabilities["Contactor_Model"] = dict(
                zip(
                    classes,
                    probability_array
                )
            )

        # --------------------------------------------------------
        # OVERLOAD
        # --------------------------------------------------------

        if self.overload_model is not None:

            probability_array = (
                self.overload_model
                .predict_proba(
                    prediction_input
                )[0]
            )

            classes = (
                self.overload_model
                .classes_
            )

            probabilities["Overload_Model"] = dict(
                zip(
                    classes,
                    probability_array
                )
            )

        return probabilities

    # ============================================================
    # DISPLAY TOP ML PREDICTIONS
    # ============================================================

    @staticmethod
    def display_top_predictions(
        probabilities,
        number_of_predictions=3
    ):

        print("\nML PREDICTION PROBABILITIES")
        print("--------------------------------")

        for component_type, values in probabilities.items():

            print(
                f"\n{component_type.replace('_', ' ')}:"
            )

            sorted_values = sorted(
                values.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for model, probability in (
                sorted_values[:number_of_predictions]
            ):

                print(
                    f"  {model}: "
                    f"{probability * 100:.1f}%"
                )

    # ============================================================
    # RECOMMEND CONFIGURATION
    # ============================================================

    def recommend(
        self,
        motor_power_kw,
        motor_current_a,
        voltage_v,
        starter_type,
        starting_type,
        coordination_type=None
    ):

        print(
            "\nSearching manufacturer configurations..."
        )

        candidates = self.dataset.copy()

        # ========================================================
        # STARTER FILTER
        # ========================================================

        candidates = candidates[
            candidates["Starter_Type"]
            .apply(self.normalize_text)
            ==
            self.normalize_text(starter_type)
        ]

        # ========================================================
        # STARTING TYPE FILTER
        # ========================================================

        candidates = candidates[
            candidates["Starting_Type"]
            .apply(self.normalize_text)
            ==
            self.normalize_text(starting_type)
        ]

        # ========================================================
        # VOLTAGE FILTER
        # ========================================================

        candidates = candidates[
            candidates["Voltage_V"].apply(
                lambda value:
                self.voltage_matches(
                    value,
                    voltage_v
                )
            )
        ]

        print(
            "Requested voltage:",
            voltage_v,
            "V"
        )

        # ========================================================
        # COORDINATION FILTER
        # ========================================================

        if coordination_type is not None:

            print(
                "Requested coordination:",
                coordination_type
            )

            candidates = candidates[
                candidates["Coordination_Type"].apply(
                    lambda value:
                    self.coordination_matches(
                        value,
                        coordination_type
                    )
                )
            ]

        # ========================================================
        # NO CANDIDATES
        # ========================================================

        if len(candidates) == 0:

            print(
                "\nNo manufacturer configuration "
                "matches the requested input."
            )

            return None, False

        print(
            "Compatible configurations found:",
            len(candidates)
        )

        candidates = candidates.copy()

        # ========================================================
        # GET ML PROBABILITIES
        # ========================================================

        probabilities = self.get_component_probabilities(
            motor_power_kw,
            motor_current_a
        )

        self.display_top_predictions(
            probabilities
        )

        # ========================================================
        # CURRENT DIFFERENCE
        # ========================================================

        candidates["Current_Difference"] = (
            candidates["Motor_Current_A"]
            -
            motor_current_a
        ).abs()

        # ========================================================
        # POWER DIFFERENCE
        # ========================================================

        candidates["Power_Difference"] = (
            candidates["Motor_Power_kW"]
            -
            motor_power_kw
        ).abs()

        # ========================================================
        # ML PROBABILITY SCORE
        # ========================================================

        candidates["ML_Probability_Score"] = 0.0

        # --------------------------------------------------------
        # Protection probability
        # --------------------------------------------------------

        if "Protection_Model" in probabilities:

            candidates[
                "Protection_Probability"
            ] = candidates[
                "Protection_Model"
            ].map(
                probabilities[
                    "Protection_Model"
                ]
            ).fillna(0)

            candidates[
                "ML_Probability_Score"
            ] += (
                candidates[
                    "Protection_Probability"
                ]
                *
                10
            )

        # --------------------------------------------------------
        # Contactor probability
        # --------------------------------------------------------

        if "Contactor_Model" in probabilities:

            candidates[
                "Contactor_Probability"
            ] = candidates[
                "Contactor_Model"
            ].map(
                probabilities[
                    "Contactor_Model"
                ]
            ).fillna(0)

            candidates[
                "ML_Probability_Score"
            ] += (
                candidates[
                    "Contactor_Probability"
                ]
                *
                10
            )

        # --------------------------------------------------------
        # Overload probability
        # --------------------------------------------------------

        if "Overload_Model" in probabilities:

            candidates[
                "Overload_Probability"
            ] = candidates[
                "Overload_Model"
            ].map(
                probabilities[
                    "Overload_Model"
                ]
            ).fillna(0)

            candidates[
                "ML_Probability_Score"
            ] += (
                candidates[
                    "Overload_Probability"
                ]
                *
                10
            )

        # ========================================================
        # FINAL RANKING SCORE
        #
        # Lower is better.
        #
        # We strongly reward configurations whose components
        # have high Random Forest probability.
        # ========================================================

        candidates["Score"] = (

            candidates[
                "Current_Difference"
            ]

            +

            0.5
            *
            candidates[
                "Power_Difference"
            ]

            -

            candidates[
                "ML_Probability_Score"
            ]
        )

        # ========================================================
        # SELECT BEST CONFIGURATION
        # ========================================================

        recommendation = (
            candidates
            .sort_values(
                by=[
                    "Score",
                    "Current_Difference",
                    "Power_Difference"
                ]
            )
            .iloc[0]
            .copy()
        )

        # ========================================================
        # REMOVE INTERNAL COLUMNS
        # ========================================================

        recommendation = recommendation.drop(
            labels=[
                "Current_Difference",
                "Power_Difference",
                "ML_Probability_Score",
                "Protection_Probability",
                "Contactor_Probability",
                "Overload_Probability",
                "Score"
            ],
            errors="ignore"
        )

        # ========================================================
        # DISPLAY FINAL RECOMMENDATION
        # ========================================================

        print("\n================================")
        print("MANUFACTURER RECOMMENDATION")
        print("================================")

        print(
            "Manufacturer:",
            recommendation["Manufacturer"]
        )

        print(
            "Motor power:",
            recommendation["Motor_Power_kW"],
            "kW"
        )

        print(
            "Motor current:",
            recommendation["Motor_Current_A"],
            "A"
        )

        print(
            "Voltage:",
            recommendation["Voltage_V"],
            "V"
        )

        print(
            "Protection:",
            recommendation["Protection_Type"]
        )

        print(
            "Protection model:",
            recommendation["Protection_Model"]
        )

        print(
            "Contactor:",
            recommendation["Contactor_Model"]
        )

        print(
            "Overload:",
            recommendation["Overload_Model"]
        )

        print(
            "Overload range:",
            recommendation["Overload_Min_A"],
            "-",
            recommendation["Overload_Max_A"],
            "A"
        )

        print(
            "Coordination:",
            recommendation["Coordination_Type"]
        )

        # ========================================================
        # ENGINEERING VALIDATION
        # ========================================================

        validation = validate_dol_configuration(
            motor_current=motor_current_a,
            voltage=voltage_v,
            starter_type=starter_type,
            recommendation=recommendation
        )

        return recommendation, validation