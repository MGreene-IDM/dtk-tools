from dtk.utils.Campaign.CampaignClass import *
from dtk.utils.Campaign.CampaignEnum import *


def change_biting_risk(cb, start_day=0,
                       risk_config={'Risk_Distribution_Type': 'FIXED_DURATION', 'Constant': 1},
                       coverage=1,
                       repetitions=1,
                       tsteps_btwn_repetitions=365,
                       target_group='Everyone',
                       trigger=None,
                       triggered_biting_risk_duration=-1,
                       nodeIDs=[],
                       node_property_restrictions=[],
                       ind_property_restrictions=[]
                       ):
    """
    Add an intervention to change individual biting risk as defined by the parameters to the config builder.

    Args:

      cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` that will receive the risk-changing intervention.
      start_day: The date on which to change biting risk.
      risk_config: The risk distribution type and distribution parameters defining the distribution from which biting
        risk will be drawn. Currently, Risk_Distribution_Type is allowed.
        
          FIXED_DURATION
            Parameter: Constant
          UNIFORM_DURATION
            Parameters Uniform_Min, Uniform_Max
          GAUSSIAN_DURATION
            Parameters Gaussian_Mean, Gaussian_Std_Dev
          EXPONENTIAL_DURATION
            Parameter Exponential_Mean
      coverage: The demographic coverage of the distribution.
      repetitions: The number of repetitions.
      tsteps_btwn_repetitions: The number of timesteps between repetitions.
      target_group: The group to target. To restrict by age, dict of {'agemin' : x, 'agemax' : y}. Default is targeting everyone.
      trigger: For triggered changes, the trigger for changing risk. Can be "Birth" or any other trigger string.
      triggered_biting_risk_duration: For triggered changes, the duration after start_day over which triggered risk-changing will happen. Default is forever.
      nodeIDs: The list of node IDs; if empty, defaults to all nodes.
      ind_property_restrictions: The individual property values to target; used with Property_Restrictions_Within_Node. For example, ``[{ "IndividualProperty1" : "PropertyValue1" }, {'IndividualProperty2': "PropertyValue2"}, ...]``
      node_property_restrictions: The node property values to target; used with NodePropertyRestrictions. For example, ``[{ "NodeProperty1" : "PropertyValue1" }, {'NodeProperty2': "PropertyValue2"}, ...]``

    .. note:: NewPropertyValue and DisqualifyingProperties have not been implemented with this intervention, though they could be useful.
    """

    risk_config = BitingRisk(**risk_config)

    risk_event = CampaignEvent(Start_Day=start_day,
                               Nodeset_Config=NodeSetAll(),
                               Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
                                   Number_Repetitions=repetitions,
                                   Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
                                   Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.Everyone,
                                   Demographic_Coverage=coverage,
                                   Intervention_Config=risk_config)
                               )

    if target_group != 'Everyone':
        risk_event.Event_Coordinator_Config.Target_Demographic = StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum.ExplicitAgeRanges # Otherwise default is Everyone
        risk_event.Event_Coordinator_Config.Target_Age_Min = target_group['agemin']
        risk_event.Event_Coordinator_Config.Target_Age_Max = target_group['agemax']

    if not nodeIDs:
        risk_event.Nodeset_Config = NodeSetAll()
    else:
        risk_event.Nodeset_Config = NodeSetNodeList(Node_List=nodeIDs)

    if node_property_restrictions:
        risk_event.Event_Coordinator_Config.Node_Property_Restrictions = node_property_restrictions

    if ind_property_restrictions:
        risk_event.Event_Coordinator_Config.Property_Restrictions_Within_Node = ind_property_restrictions

    if trigger:

        if 'birth' in trigger.lower():
            triggered_intervention = BirthTriggeredIV(
                Duration=triggered_biting_risk_duration,
                Demographic_Coverage=coverage,
                Actual_IndividualIntervention_Config=risk_config
            )

        else:
            triggered_intervention = NodeLevelHealthTriggeredIV(
                Demographic_Coverage=coverage,
                Duration=triggered_biting_risk_duration,
                Trigger_Condition_List=[trigger],
                Actual_IndividualIntervention_Config=risk_config
            )

        risk_event.Event_Coordinator_Config.Intervention_Config = triggered_intervention

        del risk_event.Event_Coordinator_Config.Demographic_Coverage
        del risk_event.Event_Coordinator_Config.Number_Repetitions
        del risk_event.Event_Coordinator_Config.Timesteps_Between_Repetitions
        del risk_event.Event_Coordinator_Config.Target_Demographic

        if ind_property_restrictions:
            del risk_event.Event_Coordinator_Config.Property_Restrictions_Within_Node
            risk_event.Event_Coordinator_Config.Intervention_Config.Property_Restrictions_Within_Node = ind_property_restrictions

    cb.add_event(risk_event)