def SelectOption(Items, Title = 'Select An Option', Options: dict = None):
    '''
    Arrow-Key Interactive Selector.
    Items: List[str] or List[Tuple[Value, Label]].
    Title: Header Text.
    Options:
        MenuWidth (int) — Menu Width, Default 50.
        Seperator (str) — Separator Character, Default '─'.
        PersistentDisplay (bool) — Whether Keep Menu Display After Selection, Default False.
    Returns: Selected Value (str).
    '''
    import sys
    import tty
    import termios

    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'MenuWidth'        : 50,
        'Seperator'        : '-',
        'PersistentDisplay': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Parsed = []
    for Item in Items:
        if isinstance(Item, tuple):
            Parsed.append({'Value': str(Item[0]), 'Label': str(Item[1])})
        else:
            Parsed.append({'Value': str(Item), 'Label': str(Item)})

    if not Parsed: raise ValueError('Items Must Not Be Empty')

    TitLine = (str(Title) + ':\r\n') if Title else ''
    SepLine = (str(Options.Seperator) * Options.MenuWidth + '\r\n') if Options.Seperator else ''
    BtmLine = f'↑/↓: Navigate{" " * (Options.MenuWidth - 26)}Enter: Select\r'

    MenuHeight    = len(Parsed) + bool(TitLine) + bool(SepLine) * 2
    SelectedIndex = 0

    def DrawMenu():
        sys.stdout.write(TitLine)
        sys.stdout.write(SepLine)
        for i, Item in enumerate(Parsed):
            if i == SelectedIndex:
                sys.stdout.write(f'\033[7m ● {Item["Label"]} \033[0m\r\n')
            else:
                sys.stdout.write(f'   {Item["Label"]}\r\n')
        sys.stdout.write(SepLine)
        sys.stdout.write(BtmLine)
        sys.stdout.flush()

    DrawMenu()

    Fd = sys.stdin.fileno()
    OldSettings = termios.tcgetattr(Fd)

    try:
        tty.setraw(Fd)
        while True:
            Ch = sys.stdin.read(1)
            if Ch == '\x1b':
                Ch2 = sys.stdin.read(1)
                if Ch2 == '[':
                    Ch3 = sys.stdin.read(1)
                    if   Ch3 == 'A': SelectedIndex = (SelectedIndex - 1) % len(Parsed)
                    elif Ch3 == 'B': SelectedIndex = (SelectedIndex + 1) % len(Parsed)
            elif Ch in ('\r', '\n'):
                break

            sys.stdout.write(f'\033[{MenuHeight}A')
            sys.stdout.write('\033[J')
            DrawMenu()
    finally:
        termios.tcsetattr(Fd, termios.TCSADRAIN, OldSettings)

    if Options.PersistentDisplay:
        print('')
    else:
        sys.stdout.write(f'\033[{MenuHeight}A')
        sys.stdout.write('\033[J')

    return Parsed[SelectedIndex]['Value']
