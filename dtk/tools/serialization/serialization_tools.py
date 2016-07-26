from __future__ import print_function
import dtk.tools.serialization.idtkFileTools as idtk
import json
import pandas as pd
import os

STATE_ADULT = 1         # implies female, I believe
STATE_INFECTED = 2
STATE_INFECTIOUS = 3

# functions need comments and/or cleaning.


def zero_infections(ser_date, ser_paths, ignore_nodeids=[], keep_humanids=[]):

    for serpath in ser_paths :
        serialization_files = [os.path.join(serpath, x) for x in os.listdir(serpath) if ('.dtk' in x and 'zero' not in x and ser_date in x)]
        for filename in serialization_files:
            root, ext = os.path.splitext(filename)
            output_filename = root + '_zero' + ext
            if output_filename in os.listdir(serpath) :
                continue
            print('Reading: {0}'.format(filename))
            header, _, _, data = idtk.read_idtk_file(filename)
            for node in data['simulation']['nodes']:
                if node['node']['externalId'] in ignore_nodeids:
                    continue
                zero_vector_infections(node)
                zero_human_infections(node, keep_humanids)
            root, ext = os.path.splitext(filename)
            output_filename = root + '_zero' + ext
            print('Writing: {0}'.format(output_filename))
            idtk.write_idtk_file(header, data, output_filename)
            del data

    return

def zero_vector_infections(node, remove=False):

    for vector_population in node['node']['m_vectorpopulations'] :
        class_name = vector_population['__class__']
        if class_name == 'VectorPopulation' or class_name == 'VectorPopulationAging':
            if not remove:
                vector_population['AdultQueues'].extend(vector_population['InfectedQueues'])
                vector_population['AdultQueues'].extend(vector_population['InfectiousQueues'])
            vector_population['InfectedQueues'] = []
            vector_population['InfectiousQueues'] = []
        elif class_name == 'VectorPopulationIndividual':
            if not remove:
                for cohort in vector_population['AdultQueues']:
                    assert(cohort['__class__'] == 'VectorCohortIndividual')
                    state = cohort['state']
                    if state == STATE_INFECTED or state == STATE_INFECTIOUS:
                        cohort['state'] = STATE_ADULT
            else:
                adults = vector_population['AdultQueues']
                vector_population['AdultQueues'] = [cohort for cohort in adults if cohort['state'] != STATE_INFECTED and cohort['state'] != STATE_INFECTIOUS]
        else:
            raise RuntimeError("Encountered unknown vector population class - '{0}'".format(class_name))

    return

def zero_human_infections(node, keep_ids) :
    for person in node['node']['individualHumans'] :
        if person['suid']['id'] not in keep_ids :
            person['infections'] = []
            person['infectiousness'] = 0
            person['m_is_infected'] = False
            person['m_female_gametocytes'] = 0
            person['m_female_gametocytes_by_strain'] = []
            person['m_male_gametocytes'] = 0
            person['m_male_gametocytes_by_strain'] = []
            person['m_gametocytes_detected'] = 0
            person['m_new_infection_state'] = 0
            person['m_parasites_detected_by_blood_smear'] = 0
            person['m_parasites_detected_by_new_diagnostic'] = 0

    return
