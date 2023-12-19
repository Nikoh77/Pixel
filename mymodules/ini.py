# This module is needed by the main and takes care of the control and generation of the
# configuration file through input requests.

import configparser
import os
from typing import Any

settings: dict[Any, Any] = {}


def iniSettingsCheck(options, config_file, logger) -> bool:
    config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'), comment_prefixes=('#', ';'),
                                       empty_lines_in_values=False, allow_no_value=False)
    config.read(config_file)
    for section in options:
        if not config.has_section(section):
            logger.info(f'Needed section {section} does not exist in your INI '
                        f'file, creating...')
            config.add_section(section)
        for option in options[section]:
            if config.has_option(section, option):
                logger.info(f'Ok, {section} {option} found.')
            else:
                config.set(
                    section,
                    option,
                    input(f'Please insert the {section} {option}: ')
                )
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    # Read INI file
    for section in config.sections():
        options = config.items(section)
        data = {}
        for option, value in options:
            if value != ('' and None):
                data[option] = value
            settings[section] = data
    if settings:
        return True
    else:
        return False


def iniStructCheck(folders, logger) -> bool:
    for folder in folders:
        if not os.path.exists(folders.get(folder)):
            os.makedirs(folders.get(folder))
    logger.info(f'Ok, all folders are in place')
    return True
