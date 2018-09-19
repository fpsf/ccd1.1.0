import os
import sys
from datetime import datetime

import numpy
import astropy.io.fits as fits
from PIL import Image, ImageDraw, ImageFont
from skimage import exposure
from libtiff import TIFFimage

software_version = "CCD Controller 1 - V 1.0"

def set_header(fitname):
    # Abrindo o arquivo
    fits_file = fits.open(fitname)
    # Escrevendo o Header
    # Can't get the temperature because have a locker locking shooter process
    # fits_file[0].header["TEMP"] = tuple(get_temperature())[3]
    fits_file[0].header["DATE"] = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')

    # Criando o arquivo final
    try:
        print("Tricat of set_header")
        # Fechando e removendo o arquivo temporario
        # fits_file.flush()
        fits_file.close()
    except OSError as e:
        print(fitname)
        print("Exception ->" + str(e))


def save_tif(img, newname, headers):
    print("Opening filename")
    img_tif = numpy.array(img, dtype=numpy.uint16)
    newname_tif = newname
    newname_tif += ".tif"
    info_tiff = []
    try:
        binning = int(headers['Binning'])
        binning += 1
    except Exception as e:
        print("Binning Type Error ->" + str(e))
        binning = " ??? "
    try:
        print("Tricat of save_tif")
        day_hour = get_date_hour_image_for_headers(str(headers['Start Time']))

        try:
            info_tiff.append('Binning: '+ str(binning) + "x" + str(binning)+';')
            info_tiff.append('CCD SET TEMP: '+ str(headers['Set Temperature'])+ ' Deg.'+';')
            info_tiff.append('CCD Temperature: '+ str(headers['Temperature']) + ' Deg.'+';')
            info_tiff.append('CCD Type: '+ str(headers['Imager ID'])+';')
            info_tiff.append('Exposure: '+ str(headers['Exposure']) + '0 ms'+';')
            info_tiff.append('Filter Label: '+ str(headers['Filter Label'])+';')
            info_tiff.append('Filter Wavelength: '+ str(headers['Filter Wavelength'])+';')
            info_tiff.append('Image Type: '+ 'TIF'+';')
            info_tiff.append('Latitude: '+ str(headers['Latitude']) + ' Deg.'+';')
            info_tiff.append('Longitude: '+ str(headers['Longitude']) + ' Deg.'+';')
            info_tiff.append('Moon Elevation: '+ str(headers['Moon Elevation']) + ' Deg.'+';')
            info_tiff.append('Moon Phase: '+ str(headers['Moon Phase']) + " %"+';')
            info_tiff.append('Site ID: '+ str(headers['Observatory'])+';')
            info_tiff.append('Start Time: '+ str(day_hour) + " UTC;")
            info_tiff.append('Sun Elevation:'+ str(headers['Sun Elevation']) + ' Deg.;')
            info_tiff.append('Version: '+ str(software_version)+'')
        except Exception as e:
            print("info.add_text: " + e)

        try:
            if sys.platform.startswith("linux"):
                imgarray = numpy.array(img_tif, dtype='uint16')
                im3 = Image.fromarray(imgarray)
                im3.save(newname_tif)
            elif sys.platform.startswith("win"):
                # imgarray = numpy.array(img_tif, dtype=numpy.int16)
                imgarray_tiff2 = numpy.asarray(img_tif, dtype=numpy.uint32)

                im3 = Image.fromarray(imgarray_tiff2)
                tiff = im3.resize((int(512), int(512)))
                imgarray_tiff2 = numpy.asarray(tiff, dtype=numpy.uint32)

                tiff2 = TIFFimage(imgarray_tiff2, description=info_tiff)
                tiff2.write_file(newname_tif, compression='lzw')
                print(info_tiff)
        except Exception as e:
            print(e)


    except Exception as e:
        print("Exception -> {}".format(e))


def save_fit(img_to_fit, newname, headers):
    newname_fit = newname
    newname_fit += ".fit"

    try:
        binning_fit = int(headers['Binning'])
        binning_fit += 1
    except Exception as e:
        print("Binning Type Error ->" + str(e))
        binning_fit = "???"

    # Criando o arquivo final
    try:
        day_hour = get_date_hour_image_for_headers(str(headers['Start Time']))
        # Abrindo o arquivo
        fits.writeto(newname_fit, img_to_fit)
        with fits.open(newname_fit, mode='update') as fits_file:
            fits_file[0].header["BINNING"] = str(binning_fit) + "x" + str(binning_fit)
            fits_file[0].header["CCD-TEMP"] = str(headers['Set Temperature']) + " Celsius degrees"
            fits_file[0].header["CCDSTEMP"] = str(headers['Temperature']) + " Celsius degrees"
            fits_file[0].header["CCDTYPE"] = str(headers['Imager ID'])
            fits_file[0].header["EXPOSURE"] = str(headers['Exposure'] + "0 ms")
            fits_file[0].header["FLT-LBL"] = str(headers['Filter Label'])
            fits_file[0].header["FLT-WAVE"] = str(headers['Filter Wavelength'])
            fits_file[0].header["IMG-TYPE"] = "FIT"
            fits_file[0].header["LATITUDE"] = str(headers['Latitude']) + " degrees"
            fits_file[0].header["LONGITUD"] = str(headers['Longitude']) + " degrees"
            fits_file[0].header["MO-ELE"] = str(headers['Moon Elevation']) + " degrees"
            fits_file[0].header["MO-PHASE"] = str(headers['Moon Phase']) + " %"
            fits_file[0].header["SITE-ID"] = str(headers['Observatory'])
            fits_file[0].header["START-T"] = str(day_hour) + " UTC"
            fits_file[0].header["SUN-ELEV"] = str(headers['Sun Elevation']) + " degrees"
            fits_file[0].header["VERS"] = str(software_version)

    except Exception as e:
        # print(newname_fit)
        print("Exception save_fit ->" + str(e))


def draw_image(img, file_name):
    """
    :param img: 
    :param file_name: 
    :return: 
    """
    hora_img, data_img = get_date_hour_image(file_name)
    filter_img, observatory_img = get_filter_observatory(file_name)

    if sys.platform.startswith("linux"):
        fontsFolder = '/usr/share/fonts/truetype'
        times_nr_Font = ImageFont.truetype(os.path.join(fontsFolder, 'Times_New_Roman_Bold.ttf'), 16)
    elif sys.platform.startswith("win"):
        fontsFolder = 'C:\\Windows\\Fonts\\'
        times_nr_Font = ImageFont.truetype(os.path.join(fontsFolder, 'Arial.ttf'), 16)

    draw = ImageDraw.Draw(img)
    draw.text((10, 10), observatory_img, fill='white', font=times_nr_Font)
    draw.text((470, 10), filter_img, fill='white', font=times_nr_Font)
    draw.text((420, 490), hora_img, fill='white', font=times_nr_Font)
    draw.text((10, 490), data_img, fill='white', font=times_nr_Font)
    del draw

    return img


def img_hist_equal(img, sref_min, sref_max):
    img = numpy.array(img, dtype=numpy.uint16)
    # Tuple = 6 & 7
    p2, p98 = numpy.percentile(img, (sref_min, sref_max))
    img_hist = exposure.rescale_intensity(img, in_range=(p2, p98))
    return img_hist


def get_date_hour(tempo):
    data = tempo[0:4] + "_" + tempo[4:6] + tempo[6:8]
    hora = tempo[9:11] + ":" + tempo[11:13] + ":" + tempo[13:15]

    return data, hora


def get_date_hour_image(tempo):
    hora_img = tempo[-10:-8] + ":" + tempo[-8:-6] + ":" + tempo[-6:-4] + " UT"
    data_img = tempo[-13:-11] + "/" + tempo[-15:-13] + "/" + tempo[-19:-15]

    return hora_img, data_img


def get_date_hour_image_for_headers(tempo):
    date_hour_header = tempo[:4] + "-" + tempo[4:6] + "-" + tempo[6:8] + " " + tempo[-6:-4] + ":" + tempo[-4:-2] + ":" \
                       + tempo[-2:]

    return date_hour_header


def get_filter_observatory(name):
    name_aux = name.split('/')[-1]
    name_filter = name_aux.split('_')[0]
    name_observatory = name_aux.split('_')[1]

    return name_filter, name_observatory


def get_observatory(name):
    name_aux = str(name).split(',')[1]
    name_aux = name_aux.replace("\'", "")
    name_aux = name_aux.replace(" ", "")

    return name_aux


