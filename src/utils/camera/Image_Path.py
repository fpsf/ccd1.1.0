from datetime import datetime

import os

import astropy.io.fits as fits

from src.utils.camera import Image_Processing
from src.utils.camera.Julian_Day import jd_to_date, date_to_jd
from src.utils.camera.Image_Headers import set_headers


def set_path():
    tempo = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    data = tempo[0:4] + "_" + tempo[4:6] + tempo[6:8]

    from src.business.configuration.configSystem import ConfigSystem
    cs = ConfigSystem()
    path = str(cs.get_image_path()) + "/"

    from src.business.configuration.configProject import ConfigProject
    ci = ConfigProject()
    name_observatory = str(ci.get_site_settings())
    name_observatory = Image_Processing.get_observatory(name_observatory)

    if int(tempo[9:11]) > 12:
        path = path + name_observatory + "_" + data + "/"
    else:
        ano = tempo[0:4]
        mes = tempo[4:6]
        dia = tempo[6:8]
        abs_julian_day = jd_to_date(date_to_jd(ano, mes, int(dia)) - 1)

        mes = abs_julian_day[1]
        dia = abs_julian_day[2]
        ano = abs_julian_day[0]

        if 0 < int(dia) < 10:
            dia = "0" + str(dia)
        if 0 < int(mes) < 10:
            mes = "0" + str(mes)

        path = path + name_observatory + "_" + str(ano) + "_" + str(mes) + str(dia) + "/"

    return path, tempo


def get_observatory(name):
    name_aux = str(name).split(',')[1]
    name_aux = name_aux.replace("/", "")
    name_aux = name_aux.replace(" ", "")

    return name_aux


def crop(dark_photo, pre, get_axis_xi, get_axis_xf,
         get_axis_yi, get_axis_yf, ignore_crop, img):
    path, tempo = set_path()

    # path, tempo = "/home/hiyoku/Imagens/images/", time.strftime('%Y%m%d_%H%M%S')

    if not os.path.isdir(path):
        os.makedirs(path)

    from src.business.configuration.configProject import ConfigProject
    ci = ConfigProject()
    site_id_name = str(ci.get_site_settings())

    site_id_name = Image_Processing.get_observatory(site_id_name)

    if dark_photo == 1:
        fn = pre + "-DARK" + "_" + site_id_name + "_" + tempo
        name = path + fn
        tifname = name + '.tif'
        tifname_final = fn + '.tif'
        fitname = name + '.fit'
        fitname_final = fn + '.fit'
    else:
        fn = pre + "_" + site_id_name + "_" + tempo
        name = path + fn
        tifname = name + '.tif'
        tifname_final = fn + '.tif'
        fitname = name + '.fit'
        fitname_final = fn + '.fit'

    try:
        os.unlink(tifname)
    except OSError:
        pass
    '''
    Create a new FITS file using the supplied data/header.
    Crop fit image
    '''
    try:
        if not ignore_crop:
            # x = width
            # y = height
            print("Cropping image.")
            print("Width: xi = " + str(get_axis_xi) + " xf = " + str(get_axis_xf))
            print("Height: yi = " + str(get_axis_yi) + " yf = " + str(get_axis_yf))
            img = img[get_axis_yi:get_axis_yf, get_axis_xi:get_axis_xf]  # cropping image
    except Exception as e:
        print("Not possible cropping image ->" + str(e))

    return path, tifname_final, fitname_final, fitname, tifname, site_id_name, tempo, img


def convert(img, image_tif, dark_photo, pre, tifname,
            site_id_name, tempo, image_fit, fitname):
    # cmd(SbigLib.PAR_COMMAND.CC_CLOSE_DEVICE.value, None, None)

    # cmd(SbigLib.PAR_COMMAND.CC_CLOSE_DRIVER.value, None, None)

    img_to_tif = img
    img_to_fit = img
    for_headers_dic = {}
    for_headers_dic = set_headers(for_headers_dic)

    try:
        if image_tif:
            print("Call set_tif")
            Image_Processing.save_tif(img_to_tif, tifname, for_headers_dic)
            if dark_photo == 1:
                fn = pre + "-DARK" + "_" + site_id_name + "_" + tempo
                nameimage_final = fn + '.tif'
            else:
                fn = pre + "_" + site_id_name + "_" + tempo
                nameimage_final = fn + '.tif'

    except Exception as e:
        print("Image .tif ERROR -> {}".format(e))

    try:
        if image_fit:
            fits.writeto(fitname, img_to_fit)
            print("Call set_header")
            # Image_Processing.set_header(fitname)
            Image_Processing.save_fit(img_to_fit, fitname, for_headers_dic)
            if dark_photo == 1:
                fn = pre + "-DARK" + "_" + site_id_name + "_" + tempo
                nameimage_final = fn + '.fit'
            else:
                fn = pre + "_" + site_id_name + "_" + tempo
                nameimage_final = fn + '.fit'

    except Exception as e:
        print("Image .fit ERROR -> {}".format(e))

    # print("Call set_png")
    # Image_Processing.save_png(img_to_png, pngname, get_level1, get_level2)

    data, hora = Image_Processing.get_date_hour(tempo)
    return data, hora, nameimage_final
