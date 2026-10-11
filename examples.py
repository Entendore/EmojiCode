"""Example programs for the Emoji Turing Machine."""


def get_example_code(name, em):
    """Get example code by name using the provided emoji map."""
    nl = em['NEWLINE']
    blank = em['BLANK']

    examples = {
        "Binary Incrementer": _binary_incrementer(em, blank),
        "Math: Binary Decrementer": _binary_decrementer(em, blank),
        "Game: Rock-Paper-Scissors": _rock_paper_scissors(em, blank),
        "Output: ASCII Box Maker": _ascii_box_maker(em, blank, nl),
        "Output: Inventory Filter": _inventory_filter(em, blank, nl),
        "Output: Battle Logger": _battle_logger(em, blank, nl),
    }

    return examples.get(name, "")


def _binary_incrementer(em, blank):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} 1 1 1 {blank} {em['TAPE_END']}\n"
        f"# Increment: flip 1s to 0s going left\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 1 0 {em['MOVE_L']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"# When blank found, write 1 and halt\n"
        f"{em['RULE_START']} {em['INIT_STATE']} {blank} 1 {em['MOVE_R']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )


def _binary_decrementer(em, blank):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} 1 0 0 0 {blank} {em['TAPE_END']}\n"
        f"# Go to end of number\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 1 1 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 0 0 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} {blank} {blank} {em['MOVE_L']} 🔵 {em['RULE_END']}\n"
        f"# Decrement: find rightmost 1\n"
        f"{em['RULE_START']} 🔵 0 1 {em['MOVE_L']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 1 0 {em['MOVE_R']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"# Underflow case\n"
        f"{em['RULE_START']} 🔵 {blank} ❌ {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )


def _rock_paper_scissors(em, blank):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} ✊ ✋ {blank} {em['TAPE_END']}\n"
        f"# Read player 1 choice\n"
        f"{em['RULE_START']} {em['INIT_STATE']} ✊ ✊ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} ✋ ✋ {em['MOVE_R']} 🟡 {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} ✌️ ✌️ {em['MOVE_R']} 🟣 {em['RULE_END']}\n"
        f"# P1=Rock outcomes (=tie, 1=P1 wins, 2=P2 wins)\n"
        f"{em['RULE_START']} 🔵 ✊ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 ✋ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 ✌️ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"# P1=Paper outcomes\n"
        f"{em['RULE_START']} 🟡 ✊ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 ✋ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 ✌️ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"# P1=Scissors outcomes\n"
        f"{em['RULE_START']} 🟣 ✊ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟣 ✋ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟣 ✌️ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )


def _ascii_box_maker(em, blank, nl):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} / - - - - - \\ {nl} | {blank} {blank} {blank} {blank} {blank} | {nl} \\ - - - - - / {em['TAPE_END']}\n"
        f"# Copy non-blank characters\n"
        f"{em['RULE_START']} {em['INIT_STATE']} / / {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} - - {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} \\ \\ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} {nl} {nl} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"# Fill blanks with stars inside box\n"
        f"{em['RULE_START']} {em['INIT_STATE']} | | {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 {blank} ⭐ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 | | {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )


def _inventory_filter(em, blank, nl):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} 🍎 🗑️ ⚔️ 🗑️ 🛡️ {em['TAPE_END']}\n"
        f"# Scan and mark items to keep\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 🍎 🍎 {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} ⚔️ ⚔️ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 🛡️ 🛡️ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 🗑️ {blank} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"# Add newlines after kept items\n"
        f"{em['RULE_START']} 🔵 🍎 {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 ⚔️ {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 🛡️ {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 🗑️ {blank} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 {blank} {blank} {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"# Restore original items (remove newlines)\n"
        f"{em['RULE_START']} 🟡 🍎 🍎 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 ⚔️ ⚔️ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 🛡️ 🛡️ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 {nl} {nl} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟡 {blank} {blank} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )


def _battle_logger(em, blank, nl):
    return (
        f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
        f"{em['TAPE_START']} 🧙 🧟 {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {blank} {em['TAPE_END']}\n"
        f"# Copy combatants\n"
        f"{em['RULE_START']} {em['INIT_STATE']} 🧙 🧙 {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵 🧟 🧟 {em['MOVE_R']} 🟡 {em['RULE_END']}\n"
        f"# Write combat symbol\n"
        f"{em['RULE_START']} 🟡 {blank} ⚔️ {em['MOVE_R']} 🟣 {em['RULE_END']}\n"
        f"# Write line break\n"
        f"{em['RULE_START']} 🟣 {blank} {nl} {em['MOVE_R']} 🟠 {em['RULE_END']}\n"
        f"# Write BAM!\n"
        f"{em['RULE_START']} 🟠 {blank} B {em['MOVE_R']} 🟤 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟤 {blank} A {em['MOVE_R']} 🟢2 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟢2 {blank} M {em['MOVE_R']} 🔵2 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵2 {blank} ! {em['MOVE_R']} 🟡2 {em['RULE_END']}\n"
        f"# Write line break\n"
        f"{em['RULE_START']} 🟡2 {blank} {nl} {em['MOVE_R']} 🟣2 {em['RULE_END']}\n"
        f"# Write winner\n"
        f"{em['RULE_START']} 🟣2 {blank} 🧙 {em['MOVE_R']} 🟠2 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟠2 {blank} W {em['MOVE_R']} 🟤2 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟤2 {blank} I {em['MOVE_R']} 🟢3 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🟢3 {blank} N {em['MOVE_R']} 🔵3 {em['RULE_END']}\n"
        f"{em['RULE_START']} 🔵3 {blank} S {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
        f"{em['PRINT']}\n"
        f"{em['RUN']}"
    )