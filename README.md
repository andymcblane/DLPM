# Off Grid Dump Load Priority Manager - DLPM 

This system is designed to be installed on top of an off-grid, lithium ion (18650) battery system, which has solar input. Voltages are configurable in config.toml, however **no considerations** have been made for the relatively flat voltage curve of other lithium battery chemistries. 

Once the solar has fully charged, there is no where to divert the excess power. This system monitors the battery voltage, and exposes HTTP endpoints per-device. e.g /pump - the response being a boolean 0 or 1 

The order of the devices in config.toml is the priority order in which they will be enabled and disabled. Additionally a minimum duration can be configued, as some devices require time to become usable or worthwhile (e.g cryto miner, A/C)

