import os
import cv2
import fitz
import numpy
import requests


from PIL import Image, ImageDraw, ImageFont


# from Download import headURL as Pkg_Download_headURL
# from Pkg.Download import headURL as Pkg_Download_headURL
from .Download import headURL as Pkg_Download_headURL


def addText(fileFolder, fileName, writeData, fontPath = None, fontSize = 0.0375, fontColor = (255, 255, 255), BGColor = (0, 0, 0, 128)):
    fileFolder = fileFolder.strip() if fileFolder.strip() != "" else "."
    fileName = fileName.strip()
    filePath = os.path.join(fileFolder, fileName)

    try:
        IMG = Image.open(filePath).convert("RGBA") # 打开图片文件
        DRW = ImageDraw.Draw(IMG) # 创建一个 ImageDraw 对象
    except Exception as errorMsg:
        return (False, str(errorMsg))
    
    if 1 < fontSize < IMG.height: # 设置字体大小
        fontSizePX = int(fontSize)
    else:
        fontSizePX = int(fontSize * IMG.height)

    if fontPath:
        try:
            FONT = ImageFont.truetype(fontPath, fontSizePX)
        except:
            defaultFontPath = "C:/Windows/Fonts/仿宋_GB2312.ttf" # Windows 系统路径
            if not os.path.exists(defaultFontPath):
                defaultFontPath = "/System/Library/Fonts/Supplemental/仿宋_GB2312.ttf" # MacOS 系统路径
            if not os.path.exists(defaultFontPath):
                defaultFontPath = "/usr/share/fonts/truetype/dejavu/仿宋_GB2312.ttf" # Linux 系统路径
            FONT = ImageFont.truetype(defaultFontPath, fontSizePX)
    else:
        defaultFontPath = "C:/Windows/Fonts/仿宋_GB2312.ttf" # Windows 系统路径
        if not os.path.exists(defaultFontPath):
            defaultFontPath = "/System/Library/Fonts/Supplemental/仿宋_GB2312.ttf" # MacOS 系统路径
        if not os.path.exists(defaultFontPath):
            defaultFontPath = "/usr/share/fonts/truetype/dejavu/仿宋_GB2312.ttf" # Linux 系统路径
        FONT = ImageFont.truetype(defaultFontPath, fontSizePX)

    # 计算文本范围
    textBox = DRW.textbbox((0, 0), f" {writeData} ", font = FONT)
    textWidth = textBox[2] - textBox[0]
    textHeight = textBox[3] - textBox[1]

    NEW = Image.new("RGBA", IMG.size, (0, 0, 0, 0))
    DRW = ImageDraw.Draw(NEW)
    DRW.rectangle([0, IMG.height - textHeight - IMG.height * 0.025, textWidth, IMG.height - IMG.height * 0.0125], fill = BGColor) # 绘制背景
    DRW.text((0, IMG.height - textHeight - IMG.height * 0.025), f" {writeData} ", font = FONT, fill = fontColor) # 绘制文本

    # 合并文本层和原始图片
    IMGWithText = Image.alpha_composite(IMG, NEW)
    IMGWithText = IMGWithText.convert("RGB")

    try:
        IMGWithText.save(filePath)
        return (True, "")
    except Exception as errorMsg:
        return (False, str(errorMsg))


def getInfo(fileFolder, fileName):
    fileFolder = fileFolder.strip() if fileFolder.strip() != "" else "."
    fileName = fileName.strip()
    filePath = os.path.join(fileFolder, fileName)
    try:
        openCVVideo = cv2.VideoCapture(filePath)
        fileHeigh = int(openCVVideo.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fileWidth = int(openCVVideo.get(cv2.CAP_PROP_FRAME_WIDTH))
        openCVVideo.release()
        fileSize = os.path.getsize(filePath)
        return (True, ""), {"height": fileHeigh, "width": fileWidth, "size": fileSize}
    except Exception as errorMsg:
        return (False, str(errorMsg)), {"height": -1, "width": -1, "size": -1}


def getInfo_Online(Type, URL):
    headInfo = {"statusCode": -1, "locationURL": "", "contentType": "", "contentLength": -1, "cookie": {}}
    fileHeigh = -1
    fileWidth = -1
    try:
        if Type == "IMAGE":
            _, headInfo = Pkg_Download_headURL(URL)

            if not 400 <= headInfo["statusCode"] <= 599:
                RSP = requests.get(URL, allow_redirects = True, stream = True)
                ARR = numpy.asarray(bytearray(RSP.content), dtype = numpy.uint8)
                openCVImage = cv2.imdecode(ARR, cv2.IMREAD_COLOR)
                fileHeigh, fileWidth, _ = openCVImage.shape

            return (True, ""), {"height": fileHeigh, "width": fileWidth, "size": headInfo["contentLength"], "headInfo": headInfo}
        elif Type == "VIDEO":
            _, headInfo = Pkg_Download_headURL(URL)

            if not 400 <= headInfo["statusCode"] <= 599:
                openCVVideo = cv2.VideoCapture()
                openCVVideo.open(URL, cv2.CAP_ANY)
                fileHeigh = int(openCVVideo.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fileWidth = int(openCVVideo.get(cv2.CAP_PROP_FRAME_WIDTH))
                openCVVideo.release()

            return (True, ""), {"height": fileHeigh, "width": fileWidth, "size": headInfo["contentLength"], "headInfo": headInfo}
        else:
            raise Exception(f"Unsupported type of {Type}")
    except Exception as errorMsg:
        return (False, str(errorMsg)), {"height": -1, "width": -1, "size": -1, "headInfo": headInfo}


def getThumbnail(fileFolder, fileName, thumbFolder, thumbName, thumbSize = (400, 300), thumbQuality = 25):

    PillowSupportFileType = ["BLP", "BMP", "DDS", "DIB", "EPS", "GIF", "ICO", "IM", "JPG", "JPEG", "JFIF", "J2K", "J2P", "JPX", "MSP", "PCX", "PNG", "APNG", "PPM", "SPIDER", "TGA", "TIFF", "TIF", "WEBP", "XBM", "CUR", "DCX", "FITS", "FLI", "FLC", "FPX", "FTEX", "GBR", "GD", "IMT", "IPTC", "NAA", "MCIDAS", "MIC", "MPO", "PCD", "PIXAR", "PSD", "SUN", "WAL", "EMF", "XPM"] # IMAGES
    OPENCVSupportFileType = ["3G2", "3GP", "ASF", "ASX", "AVI", "DIVX", "FLV", "M2TS", "M2V", "M4V", "MKV", "MOV", "MP4", "MPEG", "MPG", "MTS", "MXF", "OGV", "RM", "SWF", "WEBM", "WMV"] # VIDEO
    PyMuPDFSupportFileType = ["PDF"] # PDF
    # WORDSupportFileType = ["DOC", "DOCX", "DOCM", "DOT", "DOTX", "DOTM"] # OFFICE WORD
    # EXCELSupportFileType = ["XLS", "XLSX", "XLAM", "XLSM", "XLSB", "XLT", "XLTS", "XLTM", "CSV"] # OFFICE EXCEL
    # POWERPOINTSupportFileType = ["PPTX", "PPTM", "PPT", "POTX", "POTM", "POT", "PPSX", "PPSM", "PPSI"] # OFFICE POWERPOINT

    fileType = ([""] + fileName.split("."))[-1].upper()

    fileFolder = fileFolder.strip() if fileFolder.strip() != "" else "."
    fileName = fileName.strip()
    filePath = os.path.join(fileFolder, fileName)

    thumbFolder = thumbFolder.strip() if thumbFolder.strip() != "" else "."
    thumbName = thumbName.strip()
    thumbPath = os.path.join(thumbFolder, thumbName)

    if fileType in PillowSupportFileType:
        os.makedirs(thumbFolder, exist_ok = True)
        return getThumbnail_Pillow(filePath, thumbPath, thumbSize, thumbQuality)
    elif fileType in OPENCVSupportFileType:
        os.makedirs(thumbFolder, exist_ok = True)
        return getThumbnail_OpenCV(filePath, thumbPath, thumbSize, thumbQuality)
    elif fileType in PyMuPDFSupportFileType:
        os.makedirs(thumbFolder, exist_ok = True)
        return getThumbnail_PyMuPDF(filePath, thumbPath, thumbSize, thumbQuality)

    return (False, "Not support filetype"), ""


def getThumbnail_Pillow(filePath, thumbPath, thumbSize, thumbQuality):
    try:
        IMG = Image.open(filePath).convert("RGB")

        aspectRatio = float(IMG.width) / float(IMG.height)
        targetAspectRatio = float(thumbSize[0]) / float(thumbSize[1])

        if aspectRatio > targetAspectRatio:
            new_width = int(IMG.height * targetAspectRatio)
            left = (IMG.width - new_width) // 2
            IMG = IMG.crop((left, 0, left + new_width, IMG.height))
        else:
            new_height = int(IMG.width / targetAspectRatio)
            top = (IMG.height - new_height) // 2
            IMG = IMG.crop((0, top, IMG.width, top + new_height))

        IMG.thumbnail((min(thumbSize[0], IMG.width), min(thumbSize[1], IMG.height)))
        IMG.save(thumbPath, quality = thumbQuality, format="JPEG")
        return (True, ""), thumbPath
    except Exception as errorMsg:
        return (False, str(errorMsg)), ""


def getThumbnail_OpenCV(filePath, thumbPath, thumbSize, thumbQuality):
    try:
        openCVVideo = cv2.VideoCapture(filePath)
        Position = int(min(openCVVideo.get(cv2.CAP_PROP_FRAME_COUNT) / openCVVideo.get(cv2.CAP_PROP_FPS) * 1000, 0.05 * 1000))
        openCVVideo.set(cv2.CAP_PROP_POS_MSEC, Position)
        _, FRAME = openCVVideo.read()
        cv2.imwrite(f"{thumbPath}.OpenCV_Temp.jpeg", FRAME)
        openCVVideo.release()
    except Exception as errorMsg:
        return (False, str(errorMsg)), ""
    
    return getThumbnail_Pillow(f"{thumbPath}.OpenCV_Temp.jpeg", thumbPath, thumbSize, thumbQuality)


def getThumbnail_PyMuPDF(filePath, thumbPath, thumbSize, thumbQuality):
    try:
        PDF = fitz.open(filePath)
        PAGE = PDF[0].get_pixmap()
        IMG = Image.frombytes("RGB", [PAGE.width, PAGE.height], PAGE.samples)
        IMG.save(f"{thumbPath}.Py_Mu_PDF_Temp", format="JPEG")
        PDF.close()
    except Exception as errorMsg:
        return (False, str(errorMsg)), ""
    
    return getThumbnail_Pillow(f"{thumbPath}.Py_Mu_PDF_Temp", thumbPath, thumbSize, thumbQuality)


if __name__ == "__main__":
    fileFolder = "H:\\"
    fileName = "LOGO 2K.MP4"
    print(f"[getInfo(fileFolder, fileName)]: {getInfo(fileFolder, fileName)}")

    fileFolder = "H:\\"
    fileName = "LOGO 4K.MP4"
    print(f"[getInfo(fileFolder, fileName)]: {getInfo(fileFolder, fileName)}")

    fileFolder = "G:\\Temp File 临时文件"
    fileName = "PRESENTATION.jpg"
    print(f"[getInfo(fileFolder, fileName)]: {getInfo(fileFolder, fileName)}")

    fileFolder = "G:\\Temp File 临时文件"
    fileName = "PRESENTATION.JPG"
    print(f"[getInfo(fileFolder, fileName)]: {getInfo(fileFolder, fileName)}")