from PIL import Image
import numpy as np
import os
import imageio

# 使用最大值堆栈
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

        os.makedirs(os.path.dirname(self.outputpath), exist_ok=True)
        Image.fromarray(result).save(self.outputpath)
        thread.changeValue.emit(-1)

    def video(self, thread):
        os.makedirs(os.path.dirname(self.outputpath), exist_ok=True)

        result = None
        result_L = None

        kargs = {'macro_block_size': 8}
        with imageio.get_writer(self.outputpath, fps=25, **kargs) as video:
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

                video.append_data(np.array(Image.fromarray(result).convert('RGB')))
                thread.changeValue.emit((i + 1) / len(self.inputpathes) * 100)

        thread.changeValue.emit(-1)

    def frame(self, thread):
        os.makedirs(self.outputpath, exist_ok=True)
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

            Image.fromarray(result).save(os.path.join(self.outputpath, f"frame{i+1}.jpg"))
            thread.changeValue.emit((i + 1) / len(self.inputpathes) * 100)

        thread.changeValue.emit(-1)