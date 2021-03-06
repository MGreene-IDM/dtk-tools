import os
import re

import dtk.tools.demographics.compiledemog as compiledemog
from dtk.tools.migration import createmigrationheader
from dtk.tools.migration.LinkRatesModelGenerator import LinkRatesModelGenerator
from dtk.tools.migration.MigrationFile import MigrationFile, MigrationTypes
from . import visualize_routes


class MigrationGenerator(object):
    """
    Generate migration headers and binary files for DTK input;

    In a follow up refactor perhaps we should go further and decouple from demographics file;
    only supply the input relevant for migration; currently done in process_input(self)
    """

    def __init__(self, migration_file_name: str = './migration.bin',
                 migration_type: MigrationTypes = MigrationTypes.local,
                 link_rates_model: LinkRatesModelGenerator = None):
        """
        MigrationGenerator helps create a migration file

        Args:
            migration_file_name: What to save the migration file as. Defaults to './migration.bin'
            migration_type: What type of migration is it. See the MigrationTypes Enum for supported values
            link_rates_model: An instance of an LinkRatesModelGenerator. This will generate the rates matrix
        """

        # use "migration.bin" as the migration bin file name and save it in the working directory if user inputs an
        # empty string.
        if not migration_file_name:
            migration_file_name = "migration.bin"
        migration_file_dirname = os.path.dirname(migration_file_name)
        if migration_file_dirname:
            # Create folder to save migration bin file if user input a path that doesn't exist
            if not os.path.isdir(migration_file_dirname):
                os.mkdir(migration_file_dirname)

        self.migration_file_name = os.path.abspath(migration_file_name)
        self.migration_output_path = os.path.dirname(self.migration_file_name)
        if not isinstance(migration_type, MigrationTypes):
            raise ValueError("A MigrationTypes is required.")
        self.migration_type = migration_type

        if not isinstance(link_rates_model, LinkRatesModelGenerator):
            raise ValueError("A Link Rates Model Generator is required.")
        # setup our link rates model generator
        self.link_rates_model = link_rates_model
        self.link_rates = None

    def generate_link_rates(self):
        """
        Calls the link rates model generates. After generation, we ensure all our ids are in INT form as some of the
        generators return the dictionaries with float labels.
        
        Returns:
            None
        """
        self.link_rates = self.link_rates_model.generate()
        # ensure the ids are all ints
        self.link_rates = {
            int(node): {
                int(dest): v for dest, v in dests.items()
            } for node, dests in self.link_rates.items()
        }

    def save_migration_header(self, demographics_file_path: str):
        """
        generate migration header for DTK consumption
        Args:
            demographics_file_path:

        Returns:

        """
        # todo: the script below needs to be refactored/rewritten
        # in its current form it requires compiled demographisc file (that's not the only problem with its design)
        # to compile the demographics file need to know about compiledemog file here, which is unnecessary
        # compiledemog.py too could be refactored towards object-orientedness
        # the demographics_file_path supplied here may be different from self.demographics_file_path)
        compiledemog.main(demographics_file_path)
        createmigrationheader.main('dtk-tools', re.sub('\.json$', '.compiled.json', demographics_file_path),
                                   self.migration_file_name, self.migration_type.value)

    @staticmethod
    def save_migration_visualization(demographics_file_path, migration_header_binary_path, output_dir):
        """
        visualize nodes and migration routes and save the figure
        Args:
            demographics_file_path:
            migration_header_binary_path:
            output_dir:

        Returns:

        """
        # todo: the script below needs to be refactored
        visualize_routes.main(demographics_file_path, migration_header_binary_path, output_dir)

    def generate_migration(self, save_link_rates_as_txt: bool = False, demographics_file_path: str = None,
                           idRef: str = None):
        """
        Generation migration binary. 

        Args:
            save_link_rates_as_txt: If true, a human-readable text version of the link rates will be saved as either
             migration_file_name + '.txt' or migration_file_name with .bin replaced with .txt
            demographics_file_path: If passed, the demographics filed will be compiled and used to generator
            the migration file header. Use IdReference in demographics file as IdReference for migration json file.
            idRef: if demographics_file_path is not passed and idRef is passed, use idRef as IdReference for migration
            json file.
        Returns:
            None
        """
        self.generate_link_rates()
        # ensure link rate ids are ints

        if demographics_file_path:  # ensure we have a compiled copy
            mfile = MigrationFile(None, self.link_rates)
            compiledemog.main(demographics_file_path)
            mfile.generate_file(self.migration_file_name, route=self.migration_type,
                                compiled_demographics_file_path=re.sub('\.json$', '.compiled.json',
                                                                       demographics_file_path))
        else:
            # IdReference is a required element in migration file header
            if idRef:
                mfile = MigrationFile(idRef, self.link_rates)
                mfile.generate_file(self.migration_file_name, route=self.migration_type)
            else:
                raise ValueError("An idRef is required if you don't provide a demographics file.")

        if save_link_rates_as_txt:
            if '.bin' in self.migration_file_name:
                lr_txt_path = self.migration_file_name.replace('.bin', '.txt')
            else:
                lr_txt_path = f'{self.migration_file_name}.txt'
            mfile.save_as_txt(lr_txt_path)
