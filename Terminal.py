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

    def EnableWindowsAnsi():
        if sys.platform != 'win32': return

        try:
            import ctypes

            Kernel32 = ctypes.windll.kernel32
            Handle   = Kernel32.GetStdHandle(-11)
            Mode     = ctypes.c_uint()

            if Kernel32.GetConsoleMode(Handle, ctypes.byref(Mode)):
                Kernel32.SetConsoleMode(Handle, Mode.value | 0x0004)
        except Exception:
            pass

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

    def ReadKeyWindows():
        import msvcrt

        Ch = msvcrt.getwch()
        if Ch == '\x03': raise KeyboardInterrupt
        if Ch in ('\x00', '\xe0'):
            Ch2 = msvcrt.getwch()
            if   Ch2 == 'H': return 'UP'
            elif Ch2 == 'P': return 'DOWN'
        elif Ch in ('\r', '\n'):
            return 'ENTER'

        return None

    def ReadKeyPosix():
        Ch = sys.stdin.read(1)
        if Ch == '\x03': raise KeyboardInterrupt
        if Ch == '\x1b':
            Ch2 = sys.stdin.read(1)
            if Ch2 == '[':
                Ch3 = sys.stdin.read(1)
                if   Ch3 == 'A': return 'UP'
                elif Ch3 == 'B': return 'DOWN'
        elif Ch in ('\r', '\n'):
            return 'ENTER'

        return None

    EnableWindowsAnsi()
    DrawMenu()

    if sys.platform == 'win32':
        while True:
            Key = ReadKeyWindows()
            if   Key == 'UP'   : SelectedIndex = (SelectedIndex - 1) % len(Parsed)
            elif Key == 'DOWN' : SelectedIndex = (SelectedIndex + 1) % len(Parsed)
            elif Key == 'ENTER': break
            else               : continue

            sys.stdout.write(f'\033[{MenuHeight}A')
            sys.stdout.write('\033[J')
            DrawMenu()
    else:
        import tty
        import termios

        Fd = sys.stdin.fileno()
        OldSettings = termios.tcgetattr(Fd)

        try:
            tty.setraw(Fd)
            while True:
                Key = ReadKeyPosix()
                if   Key == 'UP'   : SelectedIndex = (SelectedIndex - 1) % len(Parsed)
                elif Key == 'DOWN' : SelectedIndex = (SelectedIndex + 1) % len(Parsed)
                elif Key == 'ENTER': break
                else               : continue

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
        sys.stdout.flush()

    return Parsed[SelectedIndex]['Value']
