from PIL import Image
import numpy as np
import os

class StarTrail:
    def __init__(self, inputpathes, outputpath, num_threads, decay):
        self.inputpathes = inputpathes
        self.outputpath = outputpath
        self.num_threads = num_threads
        self.decay = decay

    def image(self, thread):
        dirpath = "LR"
        startid = 7939
        endid = 7950
        stride = 10000
        os.makedirs("max_output", exist_ok=True)
        result = None
        result_L = None
        for i in range(startid, endid+1):
            imgpath = os.path.join(dirpath, f"IMG_{i}.jpg")
            img = Image.open(imgpath)
            img_L = img.convert('L')
            img = np.array(img)
            img_L = np.array(img_L)

            if ((i - startid) % stride == 0):
                result = img
                result_L = img_L
            else:
                idx = img_L > result_L
                result[idx] = img[idx]
                result_L[idx] = img_L[idx]

            if ((i + 1 - startid) % stride == 0) or (i == endid):
                print("save")
                Image.fromarray(result).save(f"max_output/IMG_{i}.jpg")
                print("save")
            thread.changeValue.emit((i-startid+1)/(endid-startid)*100)

        # self.num_threads = num_threads

        # self.progress_bar["maximum"] = len(inputpathes)
        # self.progress_bar["value"] = 0

        # inputpathes = natsort.natsorted(inputpathes, alg=natsort.PATH)
        # N = len(inputpathes)
        # self.outputpath = outputpath
        # self.temppath = os.path.join(outputpath, "temp")
        # os.makedirs(self.temppath, exist_ok=True)

        # result = None
        # result_L = None
        # for i, imgpath in enumerate(inputpathes):
        #     img = Image.open(imgpath)
        #     img_L = img.convert('L')
        #     img = np.array(img)
        #     img_L = np.array(img_L)

        #     if (i == 0):
        #         result = img
        #         result_L = img_L
        #     else:
        #         idx = img_L > result_L
        #         result[idx] = img[idx]
        #         result_L[idx] = img_L[idx]
        #     self.progress_bar["value"] = i+1
        #     self.progress_bar.update_idletasks()

        # Image.fromarray(result).save(os.path.join(self.outputpath, f"StarTrail.png"))
        # os.removedirs(self.temppath)

        # tk.messagebox.showinfo("完成", "导出完成")
        # self.progress_bar["value"] = 0
        # self.progress_bar.update_idletasks()

    def video(self, thread):
        pass

    def frame(self, thread):
        pass
