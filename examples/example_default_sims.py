from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import SingleSimulationBuilder
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from multiprocessing import freeze_support


def do_stuff():
    SetupParser.init(selected_block='HPC')

    exp_mgr = ExperimentManagerFactory.init()
    experiment_name = "Generic Default simluation test for tools"
    generic_defaults = ['GENERIC_SIM_SIR',
                        'GENERIC_SIM_SEIR',
                        'GENERIC_SIM_SIRS',
                        'GENERIC_SIM_SEIRS',
                        'GENERIC_SIM_SI',
                        'GENERIC_SIM_SIS',
                        'GENERIC_SIM_SIR_Vaccinations_A',
                        'GENERIC_SIM_SIR_Vaccinations_B',
                        'GENERIC_SIM_SIR_Vaccinations_C']
    for sim_example in generic_defaults:
        cb = DTKConfigBuilder.from_defaults(sim_example)
        cb.set_param("Config_Name",sim_example)
        builder = SingleSimulationBuilder()
        builder.tags['Sim_Test'] = sim_example
        exp_mgr.run_simulations(config_builder=cb,
                                exp_builder=builder,
                                exp_name=experiment_name)
    exp_mgr.wait_for_finished()
    print("Congratulations! they ran.")

if __name__ == '__main__':
    freeze_support()
    do_stuff()