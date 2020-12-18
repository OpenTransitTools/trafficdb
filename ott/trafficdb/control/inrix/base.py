from ott.utils.config_util import ConfigUtil


def ini(section='inrix'):
    if not hasattr(ini, '_INI_'):
        ini._INI_ = ConfigUtil.factory(section)
    return ini._INI_
