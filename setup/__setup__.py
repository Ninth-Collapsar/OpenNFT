from pathlib import Path
import numpy as np
import pandas as pd
import shutil
import random
import scipy.io


# -----------------------------------------------------------------------------
def set_random():
    print(f"------ Set random number as {random.randint(1, 9)}. ------")
    return


# -----------------------------------------------------------------------------
def recover():
    __dir__ = Path(__file__).absolute().parent
    __matlab__ = __dir__.parent / "opennft" / "matlab"
    __screen__ = __dir__ / "screen"

    feed_toP = __matlab__ / "nfbDispl" / "displayFeedback.m"
    feed_fromP = __screen__ / "nothing" / "displayFeedback.m"
    shutil.copyfile(feed_fromP, feed_toP)

    mainLoop_fromP = __dir__ / "original" / "mainLoopEntry.m"
    mainLoop_toP = __matlab__ / "mainLoopEntry.m"
    shutil.copyfile(mainLoop_fromP, mainLoop_toP)

    return


# -----------------------------------------------------------------------------
def find_path(namestr: str, fpath):
    s = ""
    for i in Path(fpath).iterdir():
        if i.name.lower().replace("_", "").__contains__(namestr.lower().replace("_", "")):
            return i
    return s


# -----------------------------------------------------------------------------
def read_mat(fpath, tag):
    mat_path = find_path("mainLoopData", Path(fpath).joinpath("work", "NF_Data_1"))
    if mat_path == "":
        return

    data = scipy.io.loadmat(mat_path)
    vectNFBs = data['vectBFBs']
    if vectNFBs.ndim != 2 or vectNFBs.shape[1] < 480:
        return

    scalProcTimeSeries = data['scalProcTimeSeries'][:-1, :]
    vectNFBs = data['vectNFBs']
    df = pd.concat([pd.DataFrame(scalProcTimeSeries), pd.DataFrame(vectNFBs)], ignore_index=True)
    df.to_csv(Path(fpath).joinpath("watch", f"{tag}.csv"), index=False)
    print("****** Mat saved. ******")
    return


# -----------------------------------------------------------------------------
def redemy(fpath, tag1: str, tag2: int):
    tag = f"d{tag1}t{str(tag2)}"
    Path(fpath).joinpath("watch", tag).mkdir()
    read_mat(fpath, f"{tag}.csv")
    return


# -----------------------------------------------------------------------------
def run():
    __dir__ = Path(__file__).absolute().parent
    __matlab__ = __dir__.parent / "opennft" / "matlab"
    __screen__ = __dir__ / "screen"
    feed_toP = __matlab__ / "nfbDispl" / "displayFeedback.m"
    data_path = r"E:\RT\data\subjects"

    print("====== Setup started. ======")
    pname = input(">>> Input subject name: ")
    sub_path = find_path(pname, data_path)
    if sub_path == "":
        print("====== Cannot find pname in subjects. ======")
        return

    day = input(">>> Day 1 or Day 2 (1 or 2)? ")
    task = 1
    if day == "1":
        # step 1, add random number only.
        print("------ Set this group as SMA. ------")
        feed_fromP = __screen__ / "random" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()

        # step 2, add random number and double regulation time.
        nxs = input(">>> Next step (y or n)? ")
        if nxs == "n":
            recover()
            return

        redemy(sub_path, day, task)

        print("------ Set this group as LHIP. ------")
        print("------ Choose | config_dbrg.json | in <setup>. ------")
        task += 1
        set_random()

        input(">>> Done? ")
        redemy(sub_path, day, task)

    else:
        print("------ Set all 4 groups as LHIP. ------")
        mainLoop_toP = __matlab__ / "mainLoopEntry.m"

        # step 1, add rest first and set it to be baseline, 
        # move random count to the third condition, 
        # and compare regulation with rest.
        mainLoop_fromP = __dir__ / "changed" / "mainLoopEntry.m"
        shutil.copyfile(mainLoop_fromP, mainLoop_toP)
        feed_fromP = __screen__ / "rest" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        print("------ Choose | config_rest.json | in <setup>. ------")

        # step 2, repeat step 1 and set another random count.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return

        redemy(sub_path, day, task)
        task += 1
        set_random()

        # step 3, compare with above steps, remove regulation only.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return

        redemy(sub_path, day, task)
        task += 1
        feed_fromP = __screen__ / "rest" / "rm_reg" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()

        # step 4, repeat step 1.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return

        redemy(sub_path, day, task)
        task += 1
        feed_fromP = __screen__ / "rest" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()

        input(">>> Done? ")
        redemy(sub_path, day, task)

    # recover
    recover()
    return


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run()
