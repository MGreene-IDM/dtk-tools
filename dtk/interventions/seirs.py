seirs_campaign = {
    "Events": [
        {
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 0.001,
                "Intervention_Config": {
                    "Antigen": 0,
                    "Genome": 0,
                    "Outbreak_Source": "PrevalenceIncrease",
                    "class": "OutbreakIndividual"
                },
                "Target_Demographic": "Everyone",
                "class": "StandardInterventionDistributionEventCoordinator"
            },
            "Event_Name": "Outbreak",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 1,
            "class": "CampaignEvent"
        },
        {
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "Cost_To_Consumer": 10.0,
                    "Reduced_Transmit": 0,
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "Box_Duration": 3650,
                        "Initial_Effect": 1,
                        "class": "WaningEffectBox"
                    },
                    "class": "SimpleVaccine"
                },
                "Target_Demographic": "Everyone",
                "class": "StandardInterventionDistributionEventCoordinator"
            },
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 500,
            "class": "CampaignEvent"
        }
    ],
    "Use_Defaults": 1
}
