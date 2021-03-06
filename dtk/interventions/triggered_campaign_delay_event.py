from dtk.utils.Campaign.CampaignClass import *
import random


def triggered_campaign_delay_event(config_builder, start,  nodeIDs=[], delay_distribution="FIXED_DURATION",
                                   delay_period_mean=1, delay_period_std_dev=1, delay_period_max=1,
                                   coverage=1,
                                   triggered_campaign_delay=0, trigger_condition_list=[],
                                   listening_duration=-1, event_to_send_out=None, node_property_restrictions=[],
                                   ind_property_restrictions=[], only_target_residents=True):
    if not isinstance(nodeIDs, dict):
        if nodeIDs:
            nodeIDs = NodeSetNodeList(Node_List=nodeIDs)
        else:
            nodeIDs = NodeSetAll()

    if not event_to_send_out:
        event_to_send_out = 'Random_Event_%d' % random.randrange(100000)

    event_cfg = BroadcastEvent(Broadcast_Event=event_to_send_out)

    if triggered_campaign_delay:
        if delay_distribution == 'FIXED_DURATION':
            intervention = DelayedIntervention(
                Delay_Distribution=delay_distribution,
                Delay_Period=triggered_campaign_delay,
                Coverage=coverage,
                Actual_IndividualIntervention_Configs=[event_cfg]
            )
        elif delay_distribution == 'GAUSSIAN_DURATION':
            intervention = DelayedIntervention(
                Delay_Distribution=delay_distribution,
                Delay_Period_Mean=delay_period_mean,
                Delay_Period_Std_Dev=delay_period_std_dev,
                Delay_Period_Max=delay_period_max,
                Coverage=coverage,
                Actual_IndividualIntervention_Configs=[event_cfg]
            )
    else:
        intervention = event_cfg

    triggered_delay = CampaignEvent(
        Start_Day=int(start),
        Nodeset_Config=nodeIDs,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            Intervention_Config=NodeLevelHealthTriggeredIV(
                Trigger_Condition_List=trigger_condition_list,
                Duration=listening_duration,
                Target_Residents_Only=only_target_residents,
                Node_Property_Restrictions=node_property_restrictions,
                Property_Restrictions_Within_Node=ind_property_restrictions,
                Actual_IndividualIntervention_Config=intervention
            )
        )
    )

    config_builder.add_event(triggered_delay)
    return event_to_send_out
