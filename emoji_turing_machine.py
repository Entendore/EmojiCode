"""Core Turing Machine Engine driven purely by emoji mappings."""


class EmojiTuringMachine:
    def __init__(self, emoji_map):
        self.em = emoji_map
        self.reset()

    def reset(self):
        self.tape = []
        self.head = 0
        self.state = None
        self.rules = {}
        self.halted = False
        self.output_buffer = []
        self.step_count = 0
        self.last_rule = None  # Track last matched rule for debugging

    def parse(self, code):
        self.reset()
        tokens = code.split()
        lines = code.split('\n')
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token == self.em['INIT_STATE']:
                if i + 1 < len(tokens):
                    self.state = tokens[i + 1]
                    i += 2
                    continue

            elif token == self.em['TAPE_START']:
                self.tape = []
                i += 1
                while i < len(tokens) and tokens[i] != self.em['TAPE_END']:
                    self.tape.append(tokens[i])
                    i += 1
                if not self.tape:
                    self.tape = [self.em['BLANK']]
                i += 1
                continue

            elif token == self.em['RULE_START']:
                if i + 6 < len(tokens):
                    c_state = tokens[i + 1]
                    read = tokens[i + 2]
                    write = tokens[i + 3]
                    move = tokens[i + 4]
                    n_state = tokens[i + 5]

                    d_move = 'S'
                    if move == self.em['MOVE_R']:
                        d_move = 'R'
                    elif move == self.em['MOVE_L']:
                        d_move = 'L'
                    elif move == self.em['MOVE_STAY']:
                        d_move = 'S'
                    else:
                        raise ValueError(f"Invalid move symbol: '{move}'")

                    self.rules[(c_state, read)] = (write, d_move, n_state)
                    i += 6
                    if i < len(tokens) and tokens[i] == self.em['RULE_END']:
                        i += 1
                    continue

            elif token == self.em['PRINT']:
                self.output_buffer.append(self.format_tape())
                i += 1
                continue

            i += 1

        if not self.state:
            raise ValueError("No initial state defined.")

    def format_tape(self):
        output = ""
        nl_sym = self.em.get('NEWLINE', '')
        blank_sym = self.em['BLANK']

        for sym in self.tape:
            if sym == nl_sym:
                output += "\n"
            elif sym == blank_sym:
                continue
            else:
                output += sym

        return output.strip()

    def get_tape_string(self):
        """Get full tape as string for debugging."""
        return ' '.join(self.tape)

    def step(self):
        if self.halted or self.state == self.em['HALT_STATE']:
            self.halted = True
            return False

        if self.head < 0:
            self.tape.insert(0, self.em['BLANK'])
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape.append(self.em['BLANK'])

        read_sym = self.tape[self.head]
        key = (self.state, read_sym)

        if key not in self.rules:
            self.last_rule = None
            self.halted = True
            return False

        write_sym, move, next_state = self.rules[key]
        self.last_rule = {
            'state': self.state,
            'read': read_sym,
            'write': write_sym,
            'move': move,
            'next_state': next_state
        }

        self.tape[self.head] = write_sym
        self.state = next_state
        self.step_count += 1

        if move == 'R':
            self.head += 1
        elif move == 'L':
            self.head -= 1

        if self.state == self.em['HALT_STATE']:
            self.halted = True

        return True

    def run(self, max_steps=10000):
        steps = 0
        while self.step() and steps < max_steps:
            steps += 1
        if steps == max_steps:
            raise RuntimeError(f"Exceeded maximum steps ({max_steps}) - possible infinite loop.")

    def get_stats(self):
        """Return statistics about the machine."""
        return {
            'tape_length': len(self.tape),
            'rule_count': len(self.rules),
            'step_count': self.step_count,
            'head_position': self.head,
            'is_halted': self.halted,
            'output_count': len(self.output_buffer),
            'unique_states': len(set(k[0] for k in self.rules.keys()) | {self.state})
        }