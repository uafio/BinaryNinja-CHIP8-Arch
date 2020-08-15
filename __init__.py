from binaryninja import log_info
from .chip8 import Chip8
from .view import Chip8View

Chip8.register()
Chip8View.register()
"""
Because the CHIP-8 is an interpreted language, the ROM image contains no magic constant.
If you have multiple 3rd party Architecture plugins and you want to load a non-CHIP-8 image,
I assume the loader might misinterpret the data and use the wrong loader.
Thus I recommend disabling the plugin after use.
"""
log_info("WARNING: It's recommended to disable the 'CHIP-8' plugin after use.")
