import pickle
import re


class MemoryCell():
    def __init__(self, pointer):
        self._pointer = pointer

    @staticmethod
    def create_cell_from_tuple(t):
        if t[0] == 'C':
            return CommandCell(t[1], t[2].replace('0', ''), t[3])
        else:
            return DataCell(t[1], t[2].replace('0', ''), t[3][0])

    @property
    def pointer(self):
        return self._pointer


class DataCell(MemoryCell):
    def __init__(self, pointer, name, data):
        self._name = name
        self._data = data
        super(DataCell, self).__init__(pointer)

    @property
    def name(self):
        return self._name


class CommandCell(MemoryCell):
    def __init__(self, pointer, command, arguments):
        self._command = command
        self._arguments = tuple(arguments)
        super(CommandCell, self).__init__(pointer)

    @property
    def command(self):
        return self._command

    @property
    def arguments(self):
        return self._arguments


class VirtualMachine:
    def __init__(self, src_file=None, binary_file=None):
        self._memory = []
        self.commands = {
            'write': self._write,
            'read': self._read,
            'call': self._call,
            'def': None,
            'le': self._le,
            'goto': self._goto,
            'rdc': self._reduce,
            'push': self._push,
            'swap': self._swap,
            'pop': self._pop,
            'add': self._add,
            'ret': self._return,
            'end': self._end,
        }
        if src_file:
            self._constants = {}
            self._functions = {}
            self._labels = {}
            self._registers = {'eax', 'ecx'}
            self._current_const_name = 'A'
            with open(src_file, 'r', encoding='utf-8') as f:
                # Splits avoiding quotes content
                smart_split_pattern = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
                line_number = 0
                for line in f:
                    line = line.replace('\n', '')
                    split_line = [x for x in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line) if x]
                    if not split_line:
                        self._memory.append(CommandCell(line_number, 'end', []))
                    else:
                        command = split_line[0].lower()
                        if command not in self.commands:
                            if ':' in command:
                                self._labels[
                                    command.replace(':', '')] = line_number
                                line_number -= 1
                            else:
                                raise NameError(f'Unknown command {command} on line {line_number}')
                        elif command == 'def':
                            self._functions[split_line[1].lower()] = line_number
                            continue
                        elif command == 'write':
                            if '"' in line:
                                arguments = self._preprocess_arguments([split_line[1]])
                            else:
                                arguments = split_line[1].lower().split(',')
                            self._memory.append(
                                CommandCell(line_number, command, arguments))
                        else:
                            try:
                                arguments = split_line[1].lower().split(',')
                            except IndexError:
                                arguments = []
                            arguments = self._preprocess_arguments(arguments)
                            self._memory.append(
                                CommandCell(line_number, command, arguments))
                    line_number += 1
            self._size = len(self._memory)
            processed_values = {}
            for register in self._registers:
                self._memory.append(DataCell(self._size, register, 0))
                processed_values[register] = self._size
                self._size += 1
            for const_value, const_name in self._constants.items():
                self._memory.append(DataCell(self._size, const_name, const_value))
                processed_values[const_name] = self._size
                self._size += 1
            processed_values.update(**self._functions)
            processed_values.update(**self._labels)

            for i in range(len(self._memory)):
                if isinstance(self._memory[i], CommandCell):
                    arguments = list(self._memory[i].arguments)
                    for j in range(len(arguments)):
                        if arguments[j] in processed_values:
                            arguments[j] = processed_values[arguments[j]]
                        elif arguments[j] == 'esp':
                            arguments[j] = self.esp
                    self._memory[i] = CommandCell(self._memory[i].pointer,
                                                  self._memory[i].command,
                                                  arguments)
        elif binary_file:
            with open(binary_file, 'rb') as f:
                self._memory = pickle.load(f)
            self._size = len(self._memory)
        self._pointer = 0

    memory_size = 1000
    esp = -1

    def _preprocess_arguments(self, arguments):
        for i, arg in enumerate(arguments):
            if '"' in arg:
                const = arg.replace('"', '')
                if const not in self._constants:
                    self._constants[const] = self._current_const_name
                    self._current_const_name = chr(
                        ord(self._current_const_name) + 1)
                arguments[i] = self._constants[const]
            else:
                try:
                    const = int(arg)
                    if const not in self._constants:
                        self._constants[const] = self._current_const_name
                        self._current_const_name = chr(
                            ord(self._current_const_name) + 1)
                    arguments[i] = self._constants[const]
                except ValueError:
                    pass
        return arguments

    def dump(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self._memory, f)

    def run(self):
        while self._pointer != -1:
            if isinstance(self._memory[self._pointer], CommandCell):
                cmd_func = self.commands[self._memory[self._pointer].command]
                cmd_func(*self._memory[self._pointer].arguments)
            else:
                RuntimeError("Invalid cell type")

    def _write(self, v1):
        print(str(self._memory[v1]._data))
        self._pointer += 1

    def _read(self, v1):
        self._memory[v1]._data = int(input())
        self._pointer += 1

    def _call(self, v1):
        self._memory.append(CommandCell(self._size, None, [self._pointer + 1]))
        self._size += 1
        self._pointer = v1

    def _le(self, v1, v2):
        if self._memory[v1]._data <= self._memory[v2]._data:
            self._pointer += 1
        else:
            self._pointer += 2

    def _goto(self, v1):
        self._pointer = v1

    def _reduce(self, v1):
        self._memory[v1]._data -= 1
        self._pointer += 1

    def _push(self, v1):
        self._memory.append(DataCell(self._size, None, self._memory[v1]._data))
        self._size += 1
        self._pointer += 1

    def _swap(self, v1, v2):
        self._memory[v1]._data, self._memory[v2]._data = self._memory[v2]._data, \
                                                         self._memory[v1]._data
        self._pointer += 1

    def _pop(self, v1):
        self._memory[v1]._data = self._memory.pop()._data
        self._size -= 1
        self._pointer += 1

    def _add(self, v1, v2):
        self._memory[v1]._data += self._memory[v2]._data
        self._pointer += 1

    def _return(self):
        stack_top = self._memory.pop()
        if isinstance(stack_top, CommandCell):
            self._size -= 1
            self._pointer = stack_top.arguments[0]
        else:
            raise RuntimeError()

    def _end(self):
        self._pointer = -1


src_vm = VirtualMachine(src_file='fibonacci.src')
src_vm.dump('fibonacci.bin')

bin_vm = VirtualMachine(binary_file='fibonacci.bin')
bin_vm.run()
