import pathlib, pytesseract, os, string, cv2
import numpy as np
import PySimpleGUI as sg
from matplotlib import pyplot as plt
from tkinter import Tk, messagebox
from page_dewarp import dewarp
# import naming as name

os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


images = []

#This function is used to crop out the columns on the page, contourWidth
#and contourHeight determine the amount of dilation to use. Larger numbers
#will dilate too much and blend the two columns together, while smaller
#numbers will not dilate enough and the sentences or characters will not
#properly blend together.
def findContours(image, contourWidth, contourHeight):

    tempImg = image.copy()

    #The erosionKernel and erode function are used to get rid of any noise
    #before the image is thresholded to black and white. Too much noise in the
    #image will cause the dilation to be incorrect.
    #For example, too much noise in between the columns will cause the dilation
    #to blend them together. (It is important that the columns are properly
    #separated)
    erosionKernel = np.ones((5, 5), np.uint8)

    erode = cv2.erode(tempImg, erosionKernel)

    # Performing OTSU threshold
    ret, th1 = cv2.threshold(erode, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (contourWidth, contourHeight))

    # Appplying dilation on the threshold image
    dilation = cv2.dilate(th1, rect_kernel, iterations = 1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours

#fixBrightness is only used when the program cannot find two columns, we
#found that when this happens it is usually caused by the image being either
#too bright or too dim, or the brightness causes the dilation to blend the
#columns together.
def fixBrightness(dimImage):
    h, w = dimImage.shape
    sum, a, a2, a3 =cv2.mean(dimImage)
    avg = 0.2*sum
    print(avg)
    dif = 80-avg
    print(dif)
    if dimImage is None:
        sys.exit("Could not read the image.")
    gaussian = cv2.GaussianBlur(dimImage, (0,0), 10.0)
    #creates a blurred version of the image
    unsharp = cv2.addWeighted(dimImage, 1.5, gaussian, -.5, dif, dimImage)
    # Applies blurred image as negative value to remove noise and blur
    return unsharp

#crop is the main function of the textCropping program.
#It begins by cropping the columns, making sure there are two columns cropped,
#detecting where the definitions are, finding the peak of each definition line
#and the minimum of the final line of each definition.
def crop(images, placeToSave):
    definitionImages = [[]]
    sg.change_look_and_feel("Dark Grey 1")
    i = 0

    #The images array is provided by the GUI program.
    for imagex in images:
        i += 1
        #If there is more than 1 image to go through, the progress bar displays.
        if len(images) > 1:
            sg.one_line_progress_meter('Total Progress', i, len(images), 'Values')

        #We save a copy of the image in full color and a copy grayscaled right away.
        orig_img = cv2.imread(imagex)
        img_copy = orig_img.copy()
        img = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)

        #The dimensions of the image can be very important for the scale.
        dimensionY, dimensionX = img.shape

        #If the image is large, then the scale gets adjusted.
        #Otherwise, the scale remains at 1 (to keep the original images consistent.)
        if dimensionY > 5000:
            scale = dimensionY / 3000
        else:
            scale = 1

        #The contours get found using the scale as a multiplier for the original numbers
        #(13 and 50 are what we found worked the best)
        contours = findContours(img, int(13*scale), int(50*scale))

        columns = []
        columnList = []
        # Looping through the identified contours
        # Then we check to see if the contour is large enough to be considered a column.
        columnCounter = 0
        for cnt in contours:

            
            columnLeft, columnTop, columnRight, columnBottom = cv2.boundingRect(cnt)

            #If the column is large enough, add it to the columns array.
            if columnBottom > int(500*scale) and columnRight > int(400*scale):
                columns.append([columnLeft, columnTop, columnRight, columnBottom])
                columnCounter = columnCounter + 1


        #If only one column is found, try again after a brightness fix.
        if (len(columns) == 1):
            imageCopy = img.copy()
            afterFix = fixBrightness(imageCopy)
            contours = findContours(afterFix, 13, 50)
            columnCounter = 0
            columns = []
            columnList = []
            for cnt in contours:

                columnLeft, columnTop, columnRight, columnBottom = cv2.boundingRect(cnt)

                if columnBottom > 500 and columnRight > 400:
                    columns.append([columnLeft, columnTop, columnRight, columnBottom])
                    columnCounter = columnCounter + 1


        #If only one column is found again, attempt to fix the brightness again.
        if (len(columns) == 1):
            imageCopy = img.copy()
            afterFix = fixBrightness(imageCopy)
            contours = findContours(afterFix, 2, 50)
            columnCounter = 0
            columns = []
            columnList = []
            for cnt in contours:

                columnLeft, columnTop, columnRight, columnBottom = cv2.boundingRect(cnt)

                if columnBottom > 500 and columnRight > 400:
                    columns.append([columnLeft, columnTop, columnRight, columnBottom])
                    columnCounter = columnCounter + 1

        #If only one column is found again after trying multiple times, just skip the page.
        if (len(columns) == 1):
            continue

        
        #This ensures that the column that is further to the left goes first.
        if (columns[0][0] < columns[1][0]):
            columnList.append(columns[0])
            columnList.append(columns[1])
        else:
            columnList.append(columns[1])
            columnList.append(columns[0])

        dewarpList = []
        croppedList = []
        columns = []
        #dewarp then crop again
        for cols in columnList:
            columnLeft, columnTop, columnRight, columnBottom = cols
            if (columnTop < int(25*scale)):
                columnTop = int(25*scale)
            if (columnLeft < int(25*scale)):
                columnLeft = int(25*scale)

            #Cropped2 uses the column size we found on the colored image, cropped3 on the grayscale image. Both get dewarped.
            cropped2 = orig_img[columnTop - int(25*scale):columnTop + columnBottom + int(25*scale), columnLeft - int(25*scale):columnLeft + columnRight + int(25*scale)]
            cropped3 = img[columnTop - int(25*scale):columnTop + columnBottom + int(25*scale), columnLeft - int(25*scale):columnLeft + columnRight + int(25*scale)]
            cropped2 = dewarp(cropped2)
            cropped3 = dewarp(cropped3)

            croppedList.append(cropped2)

            contours = findContours(cropped3, 4, 999)


            columnCounter = 0
            for cnt in contours:
                #Find the contours again, but this time ensure that the left side of the column is very close.
                columnLeft, columnTop, columnRight, columnBottom = cv2.boundingRect(cnt)
                if columnBottom > 400 and columnRight > 400:
                    columns.append([columnLeft, columnTop, columnRight, columnBottom])
                    columnCounter = columnCounter + 1

        #The dewarped columns get added to the dewarpList.
        dewarpList.append(columns[0])
        dewarpList.append(columns[1])
        dewarpCounter = 0

        #Then, for each column we go through this loop to find and crop definitions.
        for cols in dewarpList:

            columnLeft, columnTop, columnRight, columnBottom = cols

            #cropped is the full column, left first, then right
            cropped2 = croppedList[dewarpCounter]
            cropped2 = cropped2[columnTop + int(75*scale):columnTop + columnBottom, columnLeft:columnLeft + columnRight]

            dewarpCounter += 1
            cleanCropped = cropped2.copy()

            c2h, c2w, _ = cropped2.shape
            columnRight = c2w
            columnBottom = c2h

            rect_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))


            h, w, _ = cropped2.shape

            #This is where we first use pytesseract, which finds all of the text and data surrounding it.
            boxes = pytesseract.image_to_boxes(cropped2, config='--psm 4')

            counter = 0

            lines = [[None for x in range(5000)] for y in range(5000)]
            lineNumber = 0
            letterNumber = 0
            totalLetterCounter = 0

            definitionLineList = []
            # b is : character, left, bottom, right, top
            headwordTops = []
            headwordLeft = []

            #This is where we find the lines
            for b in boxes.splitlines():
                b = b.split(' ')

                #If there are no lines yet, start with the first item.
                if (lines[0][0] == None):
                    lines[0][0] = b
                else:
                    #Remove these characters as they get found in the noise a lot.
                    if (b[0] == '"' or b[0] == '.' or b[0] == '`' or b[0] == '~' or b[0] == '“'):
                        continue
                    #This is a check to see if we have found a new line, essentially, if the position for the letter was
                    #on the right and shoots to the left, consider it a new line.
                    elif ((int(b[1]) < 50 and int(lines[lineNumber][letterNumber][1]) > 50) or (((int(lines[lineNumber][letterNumber][4])) - int(b[4])) > 40)):
                        lineNumber += 1
                        letterNumber = 0
                        lines[lineNumber][letterNumber] = b
                    else:
                        letterNumber += 1
                        lines[lineNumber][letterNumber] = b

                totalLetterCounter += 1


            finalLineNumber = lineNumber
            definitionBottom = 0
            definitionTop = 0
            definitionCoordinates = []
            headwordStart = 0
            definitionCat = 1
            #find definition boxes
            firstLineTop = 0
            lastLineBottom = 0
            guideWord = 0

            #This is used to find the peak of the first line, lines[0].
            for k in range(len(lines[0])):
                if (lines[0][k] == None):
                    break
                if (firstLineTop == 0):
                    firstLineTop = int(lines[0][k][4])
                elif (firstLineTop < int(lines[0][k][4])):
                    firstLineTop = int(lines[0][k][4])

            #Check to see if the final line is a guide word, if so, remove it.
            if (int(lines[finalLineNumber][0][1]) > 400):
                finalLineNumber = finalLineNumber - 1
                guideWord = 1

            #Find the bottom of the final line.
            for k in range(len(lines[finalLineNumber])):
                if (lines[finalLineNumber][k] == None):
                    break
                if (lastLineBottom == 0):
                    lastLineBottom = int(lines[finalLineNumber][k][2])
                elif (lastLineBottom > int(lines[finalLineNumber][k][2])) :
                    lastLineBottom = int(lines[finalLineNumber][k][2])

            #-=-=-=-=-
            #IMPORTANT
            #-=-=-=-=-
            #This is where we find what lines have the definitions.
            alphabet_string = string.ascii_uppercase
            alphabet_list = list(alphabet_string)
            alphabet_list.append('Æ')
            for i in range(len(lines)):
                if (lines[i][0] == None):
                    break
                #-=-=-=-=-
                #IMPORTANT
                #-=-=-=-=-
                
                #We check to see if the first letter in a line is a capital letter and if it is
                #far enough to the left to be considered a definition. If it is, then take it.
                
                #You can check further into the page for definitions by changing the value 25,
                #25 is what we found works best for the normal pages.

                #A larger number would get the definitions on the pages that are warped, but only
                #on the parts that are warped too far to the right. A larger number would also
                #make straight pages miss a lot of definitions.
                if ((lines[i][0][0] in alphabet_list) and int(lines[i][0][1]) < int(25*scale)):
                    definitionLineList.append(i)
                    #If the first line is at the top of the page or column and is a headword,
                    #then the page or column starts with a headword and does not get appended
                    #to the previous page or column.
                    if ((int(firstLineTop) - int(lines[i][0][4])) < int(20*scale)):
                        headwordStart = 1
                        definitionCat = 0

            #This is find the boxes for the definitions. DefinitionTop and definitionBottom
            #both get appended once to the definitionCoordinates array for each definition.
            definitionCoordinates.append(int(firstLineTop))
            for i in range(len(definitionLineList)):
                if (headwordStart == 1):
                    headwordStart = 0
                else:
                    for j in range(len(lines[definitionLineList[i]-1])):
                        if (lines[definitionLineList[i]-1][j] == None):
                            break
                        if (definitionBottom == 0):
                            definitionBottom = int(lines[definitionLineList[i]-1][j][2])
                        else:
                            if (definitionBottom > int(lines[definitionLineList[i]-1][j][2])):
                                definitionBottom = int(lines[definitionLineList[i]-1][j][2])
                    for j in range(len(lines[definitionLineList[i]])):
                        if (lines[definitionLineList[i]][j] == None):
                            break
                        if (definitionTop == 0):
                            definitionTop = int(lines[definitionLineList[i]][j][4])
                        else:
                            if (definitionTop < int(lines[definitionLineList[i]][j][4])):
                                definitionTop = int(lines[definitionLineList[i]][j][4])
                    definitionCoordinates.append(definitionBottom)
                    definitionCoordinates.append(definitionTop)

                definitionBottom = 0
                definitionTop = 0

            definitionCoordinates.append(lastLineBottom)
            j = 0

            #Every two values in the definitionCoordinates array is one definition, hence why we divide
            #by two for the loop. The values are the bottom of the definition, and then the top of the next definition.
            #We start with the bottom because the top of the first definition is the top of the column, and the bottom
            #of the last definition is the bottom of the column.

            #every definition gets appended to the definitionImages array.
            for i in range(int(len(definitionCoordinates) / 2)):
                if ((i % 2) == 0):
                    color = (255, 255, 255)
                else:
                    color = (0,0,0)
                length = len(definitionImages)
                cropped2 = cv2.rectangle(cropped2, (0, columnBottom - definitionCoordinates[j]), (columnRight, columnBottom - definitionCoordinates[j+1]), color, 2)

                if (length == 1):
                    definitionImages[length - 1].append(cleanCropped[(columnBottom - definitionCoordinates[j]):(columnBottom - definitionCoordinates[j+1]), 0:columnRight])
                    definitionImages.append([])
                    definitionCat = 0
                else:
                    if (definitionCat == 1):
                        definitionImages[length - 2].append(cleanCropped[(columnBottom - definitionCoordinates[j]):(columnBottom - definitionCoordinates[j+1]), 0:columnRight])
                        definitionCat = 0
                    else:
                        definitionImages[length - 1].append(cleanCropped[(columnBottom - definitionCoordinates[j]):(columnBottom - definitionCoordinates[j+1]), 0:columnRight])
                        definitionImages.append([])

                j += 2

            h, w, _ = cropped2.shape

    #loop through the definitionImages and output them.
    for i in range(len(definitionImages)):
        if (len(definitionImages[i]) == 0):
            break
        if (len(definitionImages[i]) == 1):
            # print(definitionImages[i][0].size)
            if (definitionImages[i][0].size == 0):
                continue
            filename = os.path.join(placeToSave, 'f1755-%d.tif' % i)
            cv2.imwrite(filename, definitionImages[i][0])
        else:
            for l in range(len(definitionImages[i])):
                h, w, _ = definitionImages[i][l].shape
                if (h == 0 or w == 0):
                    definitionImages[i].pop(l)
                    break
            w_min = min(im.shape[1] for im in definitionImages[i])
            im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=cv2.INTER_CUBIC) for im in definitionImages[i]]
            filename = os.path.join(placeToSave, 'f1755-%d.tif' % i)
            cv2.imwrite(filename, cv2.vconcat(im_list_resize))
