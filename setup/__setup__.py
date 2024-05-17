from pathlib import Path
import shutil
import random


def set_random() -> None:
    print(f"------ Set random number as {random.randint(1, 9)}. ------")
    return


def recover():
    __dir__ = Path(__file__).absolute().parent
    __matlab__ = __dir__.parent / "opennft" / "matlab"
    __screen__ = __dir__ / "screen"
    
    feed_toP = __matlab__ / "nfbDispl" / "displayFeedback.m"
    shutil.copyfile(Path(__dir__).joinpath("original", "getVolData.m"), 
                    Path(__matlab__).joinpath("utils", "getVolData.m"))
    
    feed_fromP = __screen__ / "nothing" / "displayFeedback.m"
    shutil.copyfile(feed_fromP, feed_toP)

    mainLoop_fromP = __dir__ / "original" / "mainLoopEntry.m"
    mainLoop_toP = __matlab__ / "mainLoopEntry.m"
    shutil.copyfile(mainLoop_fromP, mainLoop_toP)

    return


def run():
    __dir__ = Path(__file__).absolute().parent
    __matlab__ = __dir__.parent / "opennft" / "matlab"
    __screen__ = __dir__ / "screen"
    
    feed_toP = __matlab__ / "nfbDispl" / "displayFeedback.m"
    
    # default as online mode.
    shutil.copyfile(Path(__dir__).joinpath("changed", "getVolData.m"), 
                    Path(__matlab__).joinpath("utils", "getVolData.m"))
    
    print("====== Setup started. ======")

    day = input(">>> Day 1 or Day 2 (1 or 2)? ")
    if day == "1":
        # step 1, add random number only.
        print("------ Set this group as SMA. ------")
        feed_fromP = __screen__ / "random" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()
        print("------ Set finished. ------")
        
        # step 2, add random number and double regulation time.
        nxs = input(">>> Next step (y or n)? ")
        if nxs == "n":
            recover()
            return
        print("------ Set this group as LHIP. ------")
        json = __screen__ / "db_reg" / "config.json"
        print("------ Choose the suitable json in <setup>. ------")
        print(f"------ {json} ------")
        set_random()

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
        json = __screen__ / "rest" / "config.json"
        print("------ Choose the suitable json in <setup>. ------")
        print(f"------ {json} ------")

        # step 2, repeat step 1 and set another random count.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return
        
        set_random()

        # step 3, compare with above steps, remove regulation only.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return
        
        feed_fromP = __screen__ / "rest" / "rm_reg" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()

        # step 4, repeat step 1.
        if input(">>> Next step (y or n)? ") == "n":
            recover()
            return
        
        feed_fromP = __screen__ / "rest" / "displayFeedback.m"
        shutil.copyfile(feed_fromP, feed_toP)
        set_random()
    
    # recover
    recover()
    return


if __name__ == "__main__":
    run()
