import itertools

import os
import traceback

import time

from simtools.Analysis.OutputParser import SimulationOutputParser
from simtools.Utilities.COMPSCache import COMPSCache
from simtools.Utilities.COMPSUtilities import COMPS_login, get_asset_files_for_simulation_id


def retrieve_data(simulation) -> None:
    """
    Simple wrapper to unpack the data coming from the process pool and pass it to the function actually doing the work.

    Args:
        simulation: The simulation to process

    Returns: Nothing

    """
    # Retrieve the global variables coming from the pool initialization
    analyzers = retrieve_data.analyzers
    cache = retrieve_data.cache
    path_mapping = retrieve_data.path_mapping

    retrieve_data_for_simulation(simulation, analyzers, cache, path_mapping)


def retrieve_data_for_simulation(simulation, analyzers, cache, path_mapping):
    from simtools.Analysis.AnalyzeManager import EXCEPTION_KEY

    # Filter first and get the filenames from filtered analysis
    filtered_analysis = [a for a in analyzers if a.filter(simulation)]
    filenames = set(itertools.chain(*(a.filenames for a in filtered_analysis)))

    # We dont have anything to do :)
    if not filtered_analysis:
        cache.set(simulation.id, None)
        return

    # The byte_arrays will associate filename with content
    byte_arrays = {}

    try:
        # Retrieval for SSMT
        if path_mapping:
            for filename in filenames:
                # Create the path by replacing the part of the path that is mounted locally
                path = os.path.join(simulation.get_path(), filename).lower()
                path = path.replace(path_mapping[1], path_mapping[0])
                path = path.replace("\\", "/")

                # Open the file
                with open(path, 'rb') as output_file:
                    byte_arrays[filename] = output_file.read()

        # Retrieval for normal HPC Asset Management
        elif simulation.experiment.location == "HPC":
            retries = 5
            while True:
                try:
                    COMPS_login(simulation.experiment.endpoint)
                    COMPS_simulation = COMPSCache.simulation(simulation.id)
                    assets = [path for path in filenames if path.lower().startswith("assets")]
                    transient = [path for path in filenames if not path.lower().startswith("assets")]
                    if transient:
                        byte_arrays.update(
                            dict(zip(transient, COMPS_simulation.retrieve_output_files(paths=transient))))
                    if assets:
                        byte_arrays.update(
                            get_asset_files_for_simulation_id(simulation.id, paths=assets, remove_prefix='Assets'))
                    break
                except ConnectionResetError as e:
                    retries -= 1
                    time.sleep(3)
                    if retries == 0:
                        raise e

        # Retrieval for local file
        else:
            for filename in filenames:
                path = os.path.join(simulation.get_path(), filename)
                with open(path, 'rb') as output_file:
                    byte_arrays[filename] = output_file.read()
    except:
        tb = traceback.format_exc()
        cache.set(EXCEPTION_KEY, "An exception has been raised during data retrieval.\n"
                                 "Simulation: {} \n"
                                 "Analyzers: {}\n"
                                 "Files: {}\n"
                                 "\n{}".format(simulation, ", ".join([a.uid for a in analyzers]), ", ".join(filenames),
                                               tb))
        return

    # Selected data will be a dict with analyzer.uid => data
    selected_data = {}
    for analyzer in filtered_analysis:
        # If the analyzer needs the parsed data, parse
        if analyzer.parse:
            try:
                data = {filename: SimulationOutputParser.parse(filename, content)
                        for filename, content in byte_arrays.items()}
            except:
                tb = traceback.format_exc()
                cache.set(EXCEPTION_KEY, "An exception has been raised during the data parsing.\n"
                                         "Simulation: {} \n"
                                         "Analyzer: {}\n"
                                         "\n{}".format(simulation, analyzer, tb))
                return
        else:
            # If the analyzer doesnt wish to parse, give the raw data
            data = byte_arrays

        # Retrieve the selected data for the given analyzer
        try:
            selected_data[analyzer.uid] = analyzer.select_simulation_data(data, simulation)
        except:
            tb = traceback.format_exc()
            cache.set(EXCEPTION_KEY, "An exception has been raised during data processing.\n"
                                     "Simulation: {} \n"
                                     "Analyzer: {}\n"
                                     "\n{}".format(simulation, analyzer, tb))
            return

    # Store in the cache
    cache.set(simulation.id, selected_data)
