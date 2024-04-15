from pathlib import Path
import random
import shutil


def run():
    """ """
    __dir__ = Path(__file__).absolute().parent
    __matlab__ = __dir__.parent / "opennft" / "matlab"
    print("====== Setup started. ======")

    group = input(">>> Need a random group (y or n)? ")
    if group == "y":
        ints = input(">>> Set an interest area: ")
        comp = input(">>> Set a compared area: ")
        print(f"------ The testee are given to {random.choice([ints, comp])}. ------")

    mode = input(">>> Online mode (y or n)? ")
    online_to = __matlab__ / "utils" / "getVolData.m"
    if mode == "y":
        online_from = __dir__ / "changed" / "getVolData.m"
    else:
        online_from = __dir__ / "original" / "getVolData.m"
    shutil.copyfile(online_from, online_to)

    image = input(">>> Does feedback need images (y or n)? ")
    image_to = __matlab__ / "nfbPreprSig" / "preprSig.m"
    if image == "y":
        image_from = __dir__ / "changed" / "preprSig.m"
    else:
        image_from = __dir__ / "original" / "preprSig.m"
    shutil.copyfile(image_from, image_to)

    print(">>> What do you want to do with the feedback screen:")
    print(">>> 1.set a random count number;")
    print(">>> 2.double regulation time;")
    print(">>> 3.add rest condition;")
    print(">>> 4.remove activity bar;")
    print(">>> 5.nothing to do.")
    __screen__ = __dir__ / "screen"
    feed_to = __matlab__ / "nfbDispl" / "displayFeedback.m"
    main_loop_to = __matlab__ / "mainLoopEntry.m"
    main_loop_from = __dir__ / "original" / "mainLoopEntry.m"
    shutil.copyfile(main_loop_from, main_loop_to)

    feed = input()
    if feed == "1":
        feed_from = __screen__ / "random" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)

    elif feed == "2":
        feed_from = __screen__ / "random" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
        json = __screen__ / "db_reg" / "config.json"
        print("------ Please choose the suitable json in <setup>. ------")
        print(f"------ {json} ------")

    elif feed == "3":
        feed_from = __screen__ / "rest" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
        main_loop_from = __dir__ / "changed" / "mainLoopEntry.m"
        shutil.copyfile(main_loop_from, main_loop_to)
        json = __screen__ / "rest" / "config.json"
        print("------ Please choose the suitable json in <setup>. ------")
        print(f"------ {json} ------")

    elif feed == "4":
        feed_from = __screen__ / "rm_reg" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
    elif feed == "5":
        feed_from = __screen__ / "nothing" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
        print("====== Setup done. ======")
        return

    random_num = random.randint(1, 9)
    print(f"------ Set random number as {random_num}. ------")
    print("====== Setup done. ======")
    return


if __name__ == "__main__":
    run()
