from PIL import Image
import numpy as np
import os

class StarTrail:
    def __init__(self, inputpathes, outputpath, decay):
        self.inputpathes = inputpathes
        self.outputpath = outputpath
        self.decay = decay

    def image(self, thread):
        result = None
        result_L = None
        for i, imgpath in enumerate(self.inputpathes):
            if i != 0:
                result = (result * self.decay).astype("uint8")
                result_L = (result_L * self.decay).astype("uint8")

            img = Image.open(imgpath)
            img_L = img.convert('L')
            img = np.array(img)
            img_L = np.array(img_L)

            if i == 0:
                result = img
                result_L = img_L
            else:
                idx = img_L > result_L
                result[idx] = img[idx]
                result_L[idx] = img_L[idx]

            thread.changeValue.emit((i + 1) / len(self.inputpathes) * 100)

        Image.fromarray(result).save(self.outputpath)
        thread.changeValue.emit(-1)

    def video(self, thread):
        pass

    def frame(self, thread):
        pass
