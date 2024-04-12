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
        random_group = random.randint(1, 10)
        ints = input(">>> Set an interest area: ")
        comp = input(">>> Set a compared area: ")
        if random_group % 2 == 0:
            print(f"------ The testee are given to {ints}. ------")
        else:
            print(f"------ The testee are given to {comp}. ------")

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
    feed_to = __matlab__ / "nfbDispl" / "displayFeedback.m"
    feed = input()
    if feed == "1":
        feed_from = __dir__ / "screen" / "random" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
        random_num = random.randint(1, 9)
        print(f"------ Set random number as {random_num}. ------")
    elif feed == "2":
        print("------ Please choose the suitable json in <setup>. ------")
    elif feed == "3":
        feed_from = __dir__ / "screen" / "rest" / "displayFeedback.m"
        print("------ Please choose the suitable json in <setup>. ------")
        shutil.copyfile(feed_from, feed_to)
    elif feed == "4":
        feed_from = __dir__ / "screen" / "nobar" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)
    elif feed == "5":
        feed_from = __dir__ / "screen" / "nothing" / "displayFeedback.m"
        shutil.copyfile(feed_from, feed_to)

    print("====== Setup done. ======")
    return


if __name__ == "__main__":
    run()
