def __Client(AK: str, SK: str, EndPoint: str, STSToken: str = None) -> object:
    '''
    Aliyun OpenAPI Client.
    '''
    from alibabacloud_tea_openapi import models as OpenApiModels
    from alibabacloud_tea_openapi.client import Client as OpenApiClient
    if STSToken:
        return OpenApiClient(OpenApiModels.Config(access_key_id = AK, access_key_secret = SK, endpoint = EndPoint, security_token = STSToken))
    else:
        return OpenApiClient(OpenApiModels.Config(access_key_id = AK, access_key_secret = SK, endpoint = EndPoint))


def __EndPoint(Product: str = None, Region: str = None, Options: dict = None) -> str:
    '''
    Aliyun OpenAPI EndPoint.
    '''
    try:    Product = Product.title()
    except: raise Exception('Invalid Product')

    try:    Region  = (Region or 'CN-HANGZHOU').lower()
    except: raise Exception('Invalid Region')

    if not Options or not isinstance(Options, dict): Options = {}

    # 操作审计 Action Trail
    # Document: https://api.aliyun.com/product/Actiontrail
    if Product == 'Actiontrail':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-shanghai-finance-1']:
            return 'actiontrail.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # API 网关 API Gateway
    # Document: https://api.aliyun.com/product/CloudAPI
    if Product == 'Apigateway':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'me-central-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1', 'cn-heyuan-acdr-1']:
            return 'apigateway.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 云账单 Billing
    # Document: https://api.aliyun.com/product/BssOpenApi
    if Product == 'Billing':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'cn-chengdu', 'cn-hongkong', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'business.aliyuncs.com'
        if Region in ['ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-5', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1']:
            return 'business.ap-southeast-1.aliyuncs.com'
        raise Exception('Invalid Region')

    # 数字证书管理服务（原SSL证书） Certificate Management Service
    # Document: https://api.aliyun.com/product/Cas
    if Product == 'Cas':
        if Region in ['cn-hangzhou']:
            return 'cas.aliyuncs.com'
        if Region in ['ap-southeast-3', 'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'me-east-1']:
            return 'cas.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 内容分发 CDN
    # Document: https://api.aliyun.com/product/Cdn
    if Product == 'Cdn':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'cn-chengdu', 'cn-hongkong', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'cdn.aliyuncs.com'
        if Region in ['ap-southeast-3', 'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-5', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1']:
            return 'cdn.ap-southeast-1.aliyuncs.com'
        raise Exception('Invalid Region')

    # 云监控 Cloud Monitor
    # Document: https://api.aliyun.com/product/Cms
    if Product == 'Cms':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-zhengzhou-jva', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'me-central-1', 'cn-beijing-finance-1', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1', 'cn-heyuan-acdr-1']:
            return 'metrics.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 全站加速 DCDN (Dynamic Route for CDN)
    # Document: https://api.aliyun.com/product/Dcdn
    if Product == 'Dcdn':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'dcdn.aliyuncs.com'
        raise Exception('Invalid Region')

    # 云解析 Cloud DNS
    # Document: https://api.aliyun.com/product/Alidns
    if Product == 'Dns':
        if Region in ['cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'alidns.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-qingdao', 'cn-wulanchabu', 'cn-beijing-finance-1']:
            return 'dns.aliyuncs.com'
        raise Exception('Invalid Region')

    # 域名服务 Domain
    # Document: https://api.aliyun.com/product/Domain
    if Product == 'Domain':
        if Region in ['cn-hangzhou']:
            return 'domain.aliyuncs.com'
        if Region in ['ap-southeast-1']:
            return 'domain-intl.aliyuncs.com'
        raise Exception('Invalid Region')

    # 数据传输 Data Transmission
    # Document: https://api.aliyun.com/product/Dts
    if Product == 'Dts':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1']:
            return 'dts.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-wulanchabu']:
            return 'dts.aliyuncs.com'
        if Region in ['cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'dts.cn-hangzhou.aliyuncs.com'
        raise Exception('Invalid Region')

    # 云服务器 Elastic Compute Service
    # Document: https://api.aliyun.com/product/Ecs
    if Product == 'Ecs':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'cn-wuhan-lr', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-zhengzhou-jva', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'na-south-1', 'eu-west-1', 'me-east-1', 'me-central-1', 'cn-beijing-finance-1', 'cn-shanghai-finance-1', 'cn-heyuan-acdr-1']:
            return 'ecs.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-hangzhou-finance']:
            return 'ecs.aliyuncs.com'
        if Region in ['cn-shenzhen-finance-1']:
            return 'ecs-cn-hangzhou.aliyuncs.com'
        raise Exception('Invalid Region')

    # 函数计算 Function Compute
    # Document: https://api.aliyun.com/product/FC-Open
    if Product == 'Fc':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1']:
            return 'fc.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-hangzhou-finance']:
            if not 'Fc.AccountId' in Options: raise Exception('Require AccountId')
            return '{AccountId}.{Region}.fc.aliyuncs.com'.format(AccountId = Options.get('Fc.AccountId'), Region = Region)
        raise Exception('Invalid Region')

    # 函数计算 3.0 Function Compute 3.0
    # Document: https://api.aliyun.com/product/FC
    if Product == 'Fcv3':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1']:
            return 'fcv3.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 移动解析 HttpDNS
    # Document: https://api.aliyun.com/product/Httpdns
    if Product == 'Httpdns':
        if Region in ['ap-southeast-1']:
            return 'httpdns.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-hangzhou']:
            return 'httpdns-api.aliyuncs.com'
        raise Exception('Invalid Region')

    # 智能媒体管理 Intelligent Media Management
    # Document: https://api.aliyun.com/product/Imm
    if Product == 'Imm':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'cn-guangzhou', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1']:
            return 'imm.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 身份管理 RAM Identity Management Service
    # Document: https://api.aliyun.com/product/Ims
    if Product == 'Ims':
        if Region in ['cn-hangzhou']:
            return 'ims.aliyuncs.com'
        raise Exception('Invalid Region')

    # 视频直播 Apsara Video Live
    # Document: https://api.aliyun.com/product/Live
    if Product == 'Live':
        if Region in ['ap-southeast-1', 'eu-central-1']:
            return 'live.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-shanghai', 'cn-shenzhen', 'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-5', 'eu-central-1', 'me-central-1']:
            return 'live.aliyuncs.com'
        raise Exception('Invalid Region')

    # 对象存储 Oss (Object Storage Service)
    # Document: https://api.aliyun.com/product/Oss
    if Product == 'Oss':
        Region = Region.removeprefix('oss-'); EndPoint = 'aliyuncs.com'

        # 公共云
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'cn-wuhan-lr', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1']:
            if Options.get('Oss.Accelerate'):
                EndPoint = ('oss-accelerate-overseas.' if Options.get('Oss.Overseas') else 'oss-accelerate.') + EndPoint
            else:
                EndPoint = ('oss-{Region}-internal.'.format(Region = Region) if Options.get('Oss.Internal') else 'oss-{Region}.'.format(Region = Region)) + EndPoint

            if Options.get('Oss.S3'): EndPoint = 's3.' + EndPoint

        # 金融云
        if Region in ['cn-hzfinance', 'cn-shanghai-finance-1-pub', 'cn-szfinance', 'cn-beijing-finance-1-pub']:
            EndPoint = ('oss-{Region}-internal.'.format(Region = Region) if Options.get('Oss.Internal') else 'oss-{Region}.'.format(Region = Region)) + EndPoint

        # 金融、政务云
        if Region in ['cn-shanghai-finance-1', 'cn-shenzhen-finance-1', 'cn-beijing-finance-1', 'cn-north-2-gov-1']:
            EndPoint = 'oss-{Region}-internal.'.format(Region = Region) + EndPoint

        if Region in ['cn-hangzhou-finance', 'cn-hzjbp']:
            EndPoint = ('oss-cn-hzjbp-a-console.' or 'oss-cn-hzjbp-b-console.' or 'oss-cn-hzjbp-a-internal.' or 'oss-cn-hzjbp-b-internal.') + EndPoint

        if EndPoint == 'aliyuncs.com': raise Exception('Invalid Region')

        return '{Bucket}.{EndPoint}'.format(Bucket = Options.get('Oss.Bucket'), EndPoint = EndPoint) if Options.get('Oss.Bucket') else EndPoint

    # P2P 内容分发 PCDN
    # Document: https://api.aliyun.com/product/Pcdn
    if Product == 'Pcdn':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'pcdn.aliyuncs.com'
        raise Exception('Invalid Region')

    # 性能测试 Performance Testing
    # Document: https://api.aliyun.com/product/PTS
    if Product == 'Pts':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'pts.aliyuncs.com'
        raise Exception('Invalid Region')

    # 云解析 Private Zone
    # Document: https://api.aliyun.com/product/Pvtz
    if Product == 'Pvtz':
        if Region in ['cn-qingdao', 'cn-hangzhou', 'ap-northeast-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'pvtz.aliyuncs.com'
        raise Exception('Invalid Region')

    # 配额中心 Quota
    # Document: https://api.aliyun.com/product/Quotas
    if Product == 'Quota':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'quotas.aliyuncs.com'
        raise Exception('Invalid Region')

    # 访问控制 Resource Access Management
    # Document: https://api.aliyun.com/product/Ram
    if Product == 'Ram':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'ram.aliyuncs.com'
        raise Exception('Invalid Region')

    # 安全加速 SCDN
    # Document: https://api.aliyun.com/product/Scdn
    if Product == 'Scdn':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'ap-northeast-1', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'scdn.aliyuncs.com'
        raise Exception('Invalid Region')
    
    # 日志服务 Simple Log Service
    # Document: https://api.aliyun.com/product/Sls
    if Product == 'Sls':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'me-central-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1']:
            return '{Region}.log.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-shenzhen-finance-1']:
            return 'cn-shenzhen-finance.log.aliyuncs.com'
        raise Exception('Invalid Region')
    
    # 安全令牌 Security Token Service
    # Document: https://api.aliyun.com/product/Sts
    if Product == 'Sts':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'cn-wuhan-lr', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'na-south-1', 'eu-west-1', 'me-east-1', 'me-central-1', 'cn-beijing-finance-1', 'cn-shanghai-finance-1']:
            return 'sts.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-hangzhou-finance', 'cn-shenzhen-finance-1']:
            return 'sts.aliyuncs.com'
        raise Exception('Invalid Region')

    # 轻量应用服务器 Simple Application Server
    # Document: https://api.aliyun.com/product/SWAS-OPEN
    if Product == 'Swas':
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-wulanchabu', 'cn-hangzhou', 'cn-shanghai', 'cn-nanjing', 'cn-fuzhou', 'cn-shenzhen', 'cn-heyuan', 'cn-guangzhou', 'cn-wuhan-lr', 'ap-southeast-6', 'ap-northeast-2', 'ap-southeast-3', 'ap-northeast-1', 'ap-southeast-7', 'cn-chengdu', 'ap-southeast-1', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-central-1']:
            return 'swas.{Region}.aliyuncs.com'.format(Region = Region)
        raise Exception('Invalid Region')

    # 云工单 Ticket
    # Document: https://api.aliyun.com/product/Workorder
    if Product == 'Workorder':
        if Region in ['ap-northeast-1', 'ap-southeast-1']:
            return 'workorder.{Region}.aliyuncs.com'.format(Region = Region)
        if Region in ['cn-qingdao', 'cn-beijing', 'cn-zhangjiakou', 'cn-huhehaote', 'cn-hangzhou', 'cn-shanghai', 'cn-shenzhen', 'ap-southeast-3', 'cn-chengdu', 'ap-southeast-5', 'cn-hongkong', 'eu-central-1', 'us-east-1', 'us-west-1', 'eu-west-1', 'me-east-1', 'cn-beijing-finance-1', 'cn-hangzhou-finance', 'cn-shanghai-finance-1', 'cn-shenzhen-finance-1']:
            return 'workorder.aliyuncs.com'
        raise Exception('Invalid Region')

    raise Exception('Invalid Product')
