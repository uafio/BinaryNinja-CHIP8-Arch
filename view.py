from binaryninja import Architecture
from binaryninja import BinaryView
from binaryninja.enums import SegmentFlag, SectionSemantics


class Chip8View(BinaryView):
    """ BinaryView is basically the loader of the image """
    name = 'ROM-Only Data'
    long_name = 'CHIP-8 Interpreter ROM'

    def __init__(self, data):
        """
        Create memory map segments for the image
        We use only the ROM data, no additional data is mapped.
        Interpreter segment is not loaded to not confuse the user when looking at the image in the hex viewer
        """
        BinaryView.__init__(self, parent_view=data, file_metadata=data.file)
        self.platform = Architecture['CHIP-8'].standalone_platform
        self.data = data
        self.add_auto_segment(0x200, len(data), 0, len(data), SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable | SegmentFlag.SegmentExecutable | SegmentFlag.SegmentContainsCode)
        self.add_user_section('ROM Data', 0x200, len(data), SectionSemantics.ReadOnlyCodeSectionSemantics)
        self.add_entry_point(0x200)
        self.get_function_at(0x200).name = 'entry'



    @classmethod
    def is_valid_for_data(cls, data):
        """
        Function called by the loader to auto-determine the BinaryView for the opened file.
        Because this is an interpreted language bytecode (VM) we have no magic value to determine ROM type.
        Hack to check file size and require the first 20 instructions to be properly disassembled.
        """
        if len(data) <= 0xe00:
            dis = Disassembler()
            for i in range(0, 40, 2):
                if not dis.disasm(data[i:i+2], 0):
                    return False
            return True
        return False

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return 0x200

