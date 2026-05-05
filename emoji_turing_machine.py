"""Core Turing Machine Engine driven purely by emoji mappings."""


class EmojiTuringMachine:
    """A Turing Machine that uses emoji symbols for its language constructs."""

    def __init__(self, emoji_map):
        """Initialize with an emoji mapping dictionary."""
        self.em = emoji_map
        self.reset()

    def reset(self):
        """Reset machine to initial state."""
        self.tape = []
        self.head = 0
        self.state = None
        self.rules = {}
        self.halted = False
        self.output_buffer = []
        self.step_count = 0
        self.last_rule = None
        self.last_written_pos = -1  # Track position of last write operation

    def parse(self, code):
        """Parse emoji code into machine rules and initial state."""
        self.reset()
        
        if not code or not code.strip():
            raise ValueError("Code is empty.")
        
        # Split by whitespace to get tokens
        tokens = code.split()
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Skip comments
            if token == '#':
                # Skip until end of line (but since we split by whitespace,
                # we need to handle this differently)
                i += 1
                continue

            # Initial state: 🟢 StateName
            if token == self.em['INIT_STATE']:
                if i + 1 < len(tokens):
                    self.state = tokens[i + 1]
                    i += 2
                    continue
                else:
                    raise ValueError("Initial state symbol found but no state name provided.")

            # Tape definition: 🎬 sym1 sym2 ... ⏹️
            elif token == self.em['TAPE_START']:
                self.tape = []
                i += 1
                while i < len(tokens) and tokens[i] != self.em['TAPE_END']:
                    self.tape.append(tokens[i])
                    i += 1
                if not self.tape:
                    self.tape = [self.em['BLANK']]
                if i < len(tokens):
                    i += 1  # Skip TAPE_END
                continue

            # Transition rule: 📜 State Read Write Move NextState 🛑
            elif token == self.em['RULE_START']:
                if i + 5 < len(tokens):
                    c_state = tokens[i + 1]
                    read = tokens[i + 2]
                    write = tokens[i + 3]
                    move = tokens[i + 4]
                    n_state = tokens[i + 5]

                    # Validate and convert move symbol
                    d_move = self._parse_move(move)

                    # Store rule - warn if overwriting
                    key = (c_state, read)
                    if key in self.rules:
                        existing = self.rules[key]
                        if existing != (write, d_move, n_state):
                            # Overwriting with different rule
                            pass
                    self.rules[key] = (write, d_move, n_state)
                    
                    i += 6
                    # Skip optional RULE_END
                    if i < len(tokens) and tokens[i] == self.em['RULE_END']:
                        i += 1
                    continue
                else:
                    raise ValueError(
                        f"Incomplete rule at token position {i}. "
                        f"Expected: 📜 State Read Write Move NextState [🛑]"
                    )

            # Print command: 🖨️
            elif token == self.em['PRINT']:
                self.output_buffer.append(self.format_tape())
                i += 1
                continue

            # Run command: 🚀
            elif token == self.em['RUN']:
                i += 1
                continue

            # Skip unknown tokens (could be part of comments or whitespace issues)
            i += 1

        if not self.state:
            raise ValueError("No initial state defined. Use 🟢 followed by a state name.")

        if not self.rules:
            raise ValueError("No transition rules defined. Use 📜 to define rules.")

    def _parse_move(self, move_symbol):
        """Convert move emoji to internal representation."""
        if move_symbol == self.em['MOVE_R']:
            return 'R'
        elif move_symbol == self.em['MOVE_L']:
            return 'L'
        elif move_symbol == self.em['MOVE_STAY']:
            return 'S'
        else:
            raise ValueError(
                f"Invalid move symbol: '{move_symbol}'. "
                f"Expected one of: {self.em['MOVE_R']} (right), "
                f"{self.em['MOVE_L']} (left), {self.em['MOVE_STAY']} (stay)"
            )

    def format_tape(self):
        """Format tape contents for output, handling newlines."""
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
        """Execute a single step. Returns True if successful, False if halted/crashed."""
        # Check if already halted
        if self.halted:
            return False
        
        # Check if in halt state
        if self.state == self.em['HALT_STATE']:
            self.halted = True
            return False

        # Extend tape if head is out of bounds
        if self.head < 0:
            self.tape.insert(0, self.em['BLANK'])
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape.append(self.em['BLANK'])

        # Read symbol at head
        read_sym = self.tape[self.head]
        key = (self.state, read_sym)

        # Look up transition rule
        if key not in self.rules:
            self.last_rule = None
            self.last_written_pos = -1
            self.halted = True
            return False

        # Apply rule
        write_sym, move, next_state = self.rules[key]
        
        self.last_rule = {
            'state': self.state,
            'read': read_sym,
            'write': write_sym,
            'move': move,
            'next_state': next_state
        }

        # Write symbol
        self.tape[self.head] = write_sym
        self.last_written_pos = self.head
        
        # Update state
        self.state = next_state
        self.step_count += 1

        # Move head
        if move == 'R':
            self.head += 1
        elif move == 'L':
            self.head -= 1
        # 'S' = stay, no movement

        # Check if we've reached halt state
        if self.state == self.em['HALT_STATE']:
            self.halted = True

        return True

    def run(self, max_steps=10000):
        """Run machine to completion or until max steps reached."""
        while not self.halted and self.step_count < max_steps:
            if not self.step():
                break
        
        if self.step_count >= max_steps and not self.halted:
            raise RuntimeError(
                f"Exceeded maximum steps ({max_steps:,}) - possible infinite loop. "
                f"Use Settings → Configure Max Steps to increase this limit."
            )

    def get_stats(self):
        """Return statistics about the machine."""
        unique_states = set(k[0] for k in self.rules.keys())
        if self.state:
            unique_states.add(self.state)
        
        return {
            'tape_length': len(self.tape),
            'rule_count': len(self.rules),
            'step_count': self.step_count,
            'head_position': self.head,
            'is_halted': self.halted,
            'output_count': len(self.output_buffer),
            'unique_states': len(unique_states)
        }