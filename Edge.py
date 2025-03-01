def CreateBrowse(Private: bool = True, Options: dict = None) -> dict:
    '''
    Create a Browse.
    '''
    import selenium.webdriver

    if not __package__:
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'DriverPath'   : r'H:\GITHUB\TOOLBOX\EdgeDriver\msedgedriver.exe',
        'UserDataPath' : r'H:\GITHUB\TOOLBOX\EdgeDriver\UserData',
        'AntiRobotPath': r'H:\GITHUB\TOOLBOX\EdgeStealth.min.js'
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Driver' : None,
        'Private': True
    }

    try:
        EdgeOptions = selenium.webdriver.EdgeOptions()

        if Private:
            EdgeOptions.add_argument('--inprivate')
            Response['Private'] = True
        else:
            EdgeOptions.add_argument('--user-data-dir=' + Options['UserDataPath'])
            Response['Private'] = False

        EdgeOptions.add_argument('--window-size=800,600')
        EdgeOptions.add_argument('--no-sandbox')
        EdgeOptions.add_argument('--disable-gpu')
        EdgeOptions.add_argument('--disable-dev-shm-usage')
        EdgeOptions.add_experimental_option('excludeSwitches', ['enable-automation'])
        EdgeOptions.add_experimental_option('useAutomationExtension', False)
        EdgeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])

        EdgeOptions.add_argument("--disable-blink-features")
        EdgeOptions.add_argument("--disable-blink-features=AutomationControlled")
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Response['Driver'] = selenium.webdriver.Edge(
            service = selenium.webdriver.edge.service.Service(executable_path = Options['DriverPath']),
            options = EdgeOptions
        )
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def CloseBrowse(Driver: object) -> dict:
    '''
    Close the Browse (Force Quit).
    '''
    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': ''
    }

    try:
        Driver.quit()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def OpenUrl(Driver: object, Url: str, Options: dict = None) -> dict:
    '''
    Open a URL.
    '''
    if not __package__:
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'ExpectedCondition': False,
        'ExpectedTitle'    : '',
        'Timeout'          : 10
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Source': '',
        'Cookie': []
    }

    try:
        Driver.get(Url)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options['ExpectedCondition']:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(Driver, Options['Timeout']).until(EC.title_contains(Options['ExpectedTitle']))
        else:
            import time
            time.sleep(Options['Timeout'])
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Response['Source'] = Driver.page_source
        Response['Cookie'] = Driver.get_cookies()
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def OpenBlank(Driver: object) -> dict:
    '''
    Open a Blank Page.
    '''
    return OpenUrl(Driver, Url = 'edge://newtab', Options = {'Timeout': 0})
