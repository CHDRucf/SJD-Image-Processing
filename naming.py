import cv2, os, pytesseract, pathlib, numpy as np, PySimpleGUI as sg, matplotlib.pyplot as plt
from tkinter import Tk, messagebox
import pkg_resources.py2_warn, string

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe";


# brightness adjustment
def increase_brightness(img, value):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def startNaming(directory):

    leave = False

    for root, dirs, filess in os.walk(directory):

        for i, file in enumerate(filess):

            if not sg.one_line_progress_meter('Naming files..', i + 1, len(filess), 'Files'):
                break

            # gets the file variable ready for the next iteration
            loc = ""

            name = os.path.join(root, file)

            # print(name)

            img = cv2.imread(name);

            img = increase_brightness(img, 100)

            # resize image
            img = cv2.resize(img, (int(img.shape[1] * 4), int(img.shape[0] * 4)), interpolation = cv2.INTER_AREA)

            # processes the image file
            # mod = cv2.dilate(mod, np.ones((3, 3), np.uint8), iterations = 1)
            # mod = cv2.medianBlur(img, 1);
            mod = cv2.erode(img, np.ones((8, 4), np.uint16))
            mod = cv2.cvtColor(mod, cv2.COLOR_BGR2GRAY)
            mod = cv2.threshold(mod, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1];

            text = pytesseract.image_to_string(mod, config = '--psm 6')

            # create a temporary file to store OCR'd information
            temp = open("TEMP.txt", "w")
            temp.write(text)
            temp.close()


            wordName = ""


            temp = open("TEMP.txt", "r")

            # avoid = ['.','-',',',
            #  '[', ')', '(',
            #   '}', '{', ']',
            #    ':', ';', '?',
            #     '"', '\'', '\\',
            #      '\n', '\t', '\r',
            #       '/', '|', '*', '&',
            #        '^', '%', '$', '#',
            #        '0', '1', '2', '3',
            #        '4', '5', '6', '7',
            #        '8', '9', '!', '@',
            #        '+', '~', '=', '—',
            #          '_', '<', '>', '\'']

             # allow = list(string.ascii_lowercase)
             #
             # allow.append('\'')

            # get the name of the headword
            while 1:
                val = temp.read(1)

                if len(val) == None or val == '':
                    break


                # print("Char: "+val+"  isalpha == "+str(val.isalpha()))

                if val.isalpha():
                    wordName += val.lower()

                else:
                    temp.close()

                    break;

            # print("\n\n"+wordName+"\n\n")

            # os.replace(directory+('/f1755-%d.tif' % i), directory+("/f1755-"+wordName+".tif"))


            if not(os.path.exists(directory+("/f1755-"+wordName+".tif"))):
                os.rename(name, (directory+("/f1755-"+wordName+".tif")))


            else:
                times = 0

                while 1:
                    if not(os.path.exists((directory+("/f1755-"+wordName +"-"+ str(times) + ".tif")))):
                        os.rename(name, (directory+("/f1755-"+wordName +"-" + str(times) + ".tif")))
                        break

                    else:
                        times += 1

            # print("\nCompleted processing the file!\n");

    os.remove("TEMP.txt")

    done = Tk()
    done.withdraw()
    done = messagebox.showinfo('Done','Done!')

def main():
    startNaming(os.getcwd())

if __name__ == '__main__':
    main()
