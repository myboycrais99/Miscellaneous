import cv2
import os
import time

pos_dir = "samples/missiles/tow/positive_images"
pos_file = pos_dir + "/positive.txt"

neg_dir = "samples/missiles/tow/negative_images"
neg_file = neg_dir + "/negative.txt"

do_pos = False
do_neg = False
do_vec = True

num_pos = 225
num_neg = 3158

if do_pos is True:
    with open(pos_file, 'w') as f:
        for i in range(num_pos + 1):

            img = cv2.imread("{}/{}.jpg".format(pos_dir, i), 0)
            img_small = cv2.resize(img, (75, 50))
            bbox = cv2.selectROI(img_small, False)

            cv2.imwrite("{}/tmp/{}.jpg".format(pos_dir, i), img_small)

            print("positive_images/{}.jpg 1 {} {} {} {}".format(
                i, bbox[0], bbox[1], bbox[2], bbox[3]))

            f.write("{}/{}.jpg 1 {} {} {} {}\n".format(
                pos_dir, i, bbox[0], bbox[1], bbox[2], bbox[3]))
            # cv2.waitKey(0)
    #
    cv2.destroyAllWindows()

if do_neg is True:
    with open(neg_file, 'w') as f:
        for i in range(num_neg + 1):
            f.write("{}/{}.jpg\n".format(neg_dir, i))
    # from shutil import copyfile
    # contents = sorted(os.listdir(neg_dir))

    # cnt = 0
    # with open(neg_file, 'w') as f:
        # for name in contents:
        #     try:
        #         if name.split(".")[1] == "jpg":
        #             f.write("{}/{}\n".format(neg_dir, name))
        #             # copyfile("{}/{}".format(neg_dir, name), "{}/tmp/{}.jpg".format(neg_dir, cnt))
        #             cnt += 1
        #     except IndexError:
        #         print("error:", name)

        # for i in range(num_neg + 1):
        #     f.write("{}/{}.jpg\n".format(neg_dir, i))
            # img = cv2.imread("{}/{}.jpg".format(neg_dir, i), 0)
            # img_small = cv2.resize(img, (75, 50))
            # cv2.imwrite("{}/tmp/{}.jpg".format(neg_dir, i), img_small)


if do_vec is True:
    with open("samples/missiles/tow/go.bat", "w") as f:
        num_samples = 5000
        for i in range(num_pos + 1):
            f.write(r"opencv_createsamples.exe "
                    r"-info positive.txt -vec samples{}.vec -bg negative.txt "
                    r" -w 75 -h 50 " # -num {}
                    r"-maxxangle 1 -maxyangle 1 -maxzangle 1 -randinv "
                    r"-img positive_images\{}.jpg PAUSE"
                    "\n\n".format(i, i))

    print("running bat...")
    os.chdir(r"samples\missiles\tow")
    os.system(r"go.bat")

    time.sleep(1)
    os.system(r"python mergevec.py -v ./ "
              r"-o all_samples.vec")

# for i in range(2):
#     os.system(r"samples\missiles\tow\opencv_createsamples.exe "
#               r"-info positive.txt -vec samples\missiles\tow\samples{}.vec -num 10 "
#               r"-w 75 -h 50 -img positive_images\{}.jpg "
#               r"-maxxangle 1 -maxyangle 1 -maxzangle 1 -randinv "
#               r"-bg negative.txt PAUSE".format(i, i))

    # print(subprocess.call(r"samples\missiles\tow\opencv_createsamples.exe -info positive.txt -vec samples1.vec -num 10 -w 75 -h 50 -img positive_images\0.jpg -bg negative.txt"))
