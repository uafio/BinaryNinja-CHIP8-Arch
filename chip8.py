from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import Endianness, InstructionTextTokenType, BranchType, SegmentFlag, SectionSemantics
from binaryninja.log import log_info
from .view import Chip8View
from .disasm import Disassembler


class Chip8(Architecture):
    name = 'CHIP-8'
    endianness = Endianness.BigEndian
    address_size = 2
    default_int_size = 2
    instr_alignment = 2
    max_instr_length = 2
    opcode_display_length = 2
    regs = {
        'PC': RegisterInfo('PC', 2),
        'SP': RegisterInfo('SP', 1),
        'I': RegisterInfo('I', 2),

        'DT': RegisterInfo('DT', 1),
        'ST': RegisterInfo('ST', 1),

        'V0': RegisterInfo('V0', 1),
        'V1': RegisterInfo('V1', 1),
        'V2': RegisterInfo('V2', 1),
        'V3': RegisterInfo('V3', 1),
        'V4': RegisterInfo('V4', 1),
        'V5': RegisterInfo('V5', 1),
        'V6': RegisterInfo('V6', 1),
        'V7': RegisterInfo('V7', 1),
        'V8': RegisterInfo('V8', 1),
        'V9': RegisterInfo('V9', 1),
        'Va': RegisterInfo('Va', 1),
        'Vb': RegisterInfo('Vb', 1),
        'Vc': RegisterInfo('Vc', 1),
        'Vd': RegisterInfo('Vd', 1),
        'Ve': RegisterInfo('Ve', 1),
        'Vf': RegisterInfo('Vf', 1)
    }
    stack_pointer = 'SP'

    def __init__(self):
        super().__init__()
        self.dis = Disassembler()

    def get_instruction_info(self, data, addr):
        """ Establishes instruction length and branch info """
        if len(data) > 2:
            data = data[:2]
        result = InstructionInfo()
        result.length = 2
        vars = self.dis._vars(data)
        baddr = vars['addr']
        binfo = self.dis.get_branch_info(data)
        if binfo == BranchType.UnconditionalBranch or binfo == BranchType.CallDestination:
            result.add_branch(binfo, baddr)
        elif binfo == BranchType.FunctionReturn or binfo == BranchType.IndirectBranch:
            result.add_branch(binfo)
        elif binfo == BranchType.TrueBranch:
            result.add_branch(BranchType.TrueBranch, addr + 4)
            result.add_branch(BranchType.FalseBranch, addr + 2)
        elif binfo == BranchType.FalseBranch:
            result.add_branch(BranchType.TrueBranch, addr + 4)
            result.add_branch(BranchType.FalseBranch, addr + 2)
        return result
    
    def get_instruction_text(self, data, addr):
        """ Display text for tokanized instruction """
        if len(data) > 2:
            data = data[:2]
        tokens = self.dis.disasm(data, addr)
        if not tokens:
            tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, '_emit'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(data[0]), data[0]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(data[1]), data[1])]
        return tokens, 2

    def get_instruction_low_level_il(self, data, addr, il):
        """ TODO: Implement a lifter here """
        return None







