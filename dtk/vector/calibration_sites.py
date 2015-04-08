from dtk.generic.geography import set_geography
from dtk.generic.demographics import add_immune_overlays
from dtk.vector.input_EIR_by_site import configure_site_EIR
from dtk.utils.reports.health_seeking import add_health_seeking
from dtk.utils.reports.malaria_summary import add_summary_report
from dtk.utils.malaria_survey import add_survey
from dtk.interventions.malaria_challenge import add_challenge_trial

# In this module, we'll be building up a set of ConfigBuilder-modifying functions
# appropriate to different categories of calibration sites:
# viz. prevalence, incidence, density, malariatherapy, infectiousness
prevalence_sites = ['Matsari','Rafin_Marke','Sugungum','Namawala']
incidence_sites  = ['Dielmo','Ndiop']
density_sites    = ['Dapelogo','Laye']

# Common configuration setup
def site_setup_fn(duration=21915):
    def fn(cb,duration=duration):
        cb.update_params({ 'Simulation_Duration' : duration,
                           'Infection_Updates_Per_Timestep' : 8 })

# Configure site with correct InputEIR
def site_input_eir_fn(site,birth_cohort=True):
    def fn(cb,site=site,birth_cohort=birth_cohort):
        configure_site_EIR(cb,site=site,birth_cohort=birth_cohort)
    return fn

# Configure summary report
fine_age_bins = [ 0.08333, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                  11, 12, 13, 14, 15, 20, 25, 30, 40, 50, 60, 100 ]

def summary_report_fn(start=1,interval=365,nreports=2000,age_bins=[1000],description='Annual_Report'):
    def fn(cb,start=start,interval=interval,nreports=nreports, description=description,age_bins=age_bins):
        add_summary_report(cb, start=start, interval=interval, nreports=nreports, description=description,age_bins=age_bins)
    return fn

# Add clinical-episode-triggered treatment
default_targets=[{'trigger':'NewClinicalCase','coverage':0.8,'seek':0.6,'rate':0.2}]

def add_treatment_fn(start=0,drug=['Artemether', 'Lumefantrine'],targets=default_targets):
    def fn(cb,start=start,drug=drug,targets=targets):
        add_health_seeking(cb,start=start,drug=drug,targets=targets)
        cb.update_params({'PKPD_Model' : 'CONCENTRATION_VERSUS_TIME'})
    return fn

# Add detailed malaria patient survey
def survey_report_fn(days,interval=10000,nreports=1,coverage=1):
    def fn(cb,days=days,interval=interval,nreports=nreports,coverage=coverage):
        add_survey(cb,survey_days=days,reporting_interval=interval,nreports=nreports,coverage=coverage)
    return fn

# Add initial immunity
def add_immunity_fn(tags):
    def fn(cb,tags=tags):
        add_immune_overlays(cb,tags=tags)
    return fn

# Fill site-specific lists of setup functions, each of the template: function(ConfigBuilder)
setup_functions={}
for site in prevalence_sites:
    setup_functions[site] = [ site_setup_fn(),
                              site_input_eir_fn(site),
                              summary_report_fn() ]
for site in incidence_sites:
    setup_functions[site] = [ site_setup_fn(),
                              site_input_eir_fn(site),
                              summary_report_fn(age_bins=fine_age_bins) ]
for site in density_sites:
    setup_functions[site] = [ site_setup_fn(),
                              site_input_eir_fn(site),
                              summary_report_fn(interval=30.42,description='Monthly Report'),
                              add_treatment_fn() ]

setup_functions['Malariatherapy'] = [ site_setup_fn(duration=365),
                                      set_geography('Malariatherapy'),
                                      add_challenge_trial,
                                      survey_report_fn(days=[1]) ]

setup_functions['BFinf'] = [ site_setup_fn(duration=1461),
                             site_input_eir_fn('Dapelogo',birth_cohort=False),
                             add_immunity_fn(['150113_calib9']),
                             add_treatment_fn(),
                             survey_report_fn(days=[730]) ]

'''
    "BFinf" :        { 
                       'Demographic_Coverage' : 0.95,
                       'Base_Gametocyte_Production_Rate' : 0.1,
                       "Gametocyte_Stage_Survival_Rate": 0.58,
                       'Antigen_Switch_Rate' : 2.83e-10,
                       'Falciparum_PfEMP1_Variants' : 1114,
                       'Falciparum_MSP_Variants' : 42,
                       'MSP1_Merozoite_Kill_Fraction' : 0.46,
                       'Falciparum_Nonspecific_Types' : 46,
                       'Nonspecific_Antigenicity_Factor' : 0.32,
                       'Max_Individual_Infections' : 3
                     }
'''

def set_calibration_site(cb,site):
    for fn in setup_functions[site]:
        fn(cb)