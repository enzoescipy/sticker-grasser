import sys
import subprocess
import copy


def liveprint_exec(command_list):
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        print(c.decode("ascii"), sep="",end="")

def batfunc(argvList):
    if argvList[0] == "exit" :
        print("escape activated.")
        raise()
    if argvList[0] == "add":
        liveprint_exec([r"autogit\add.bat"])
        return
    while len(argvList) != 0:
        arg = argvList.pop(0)
        if arg != "commit" and arg != "push":
            print("invalid parameter. (wrong words or sequences) \n\n\n")
            return
        
        print(arg, argvList)
        follows = []
        if len(argvList) >= 2 and argvList[1] != "commit" and argvList[1] != "push":
            follows.append(argvList.pop(0))
            follows.append(argvList.pop(0))
        elif argvList[0] != "commit" and argvList[0] != "push":
            follows.append(argvList.pop(0))

        if len(follows) == 2 and follows[0] == "docker" and follows[1] == "git":
            follows = ["git", "docker"]

        print(arg, argvList, follows)
        if arg == "commit":
            for follow in follows :
                if follow == "docker":
                    print("commit docker execute.")
                    liveprint_exec(["autogit\commit_docker.bat"])
                elif follow == "git" : 
                    print("commit git execute.")
                    description = input("commit description for github repository : ")
                    liveprint_exec(["autogit\commit_git.bat", description])
                else:
                    print("invalid parameter. \n\n\n")
                    return
        elif arg == "push":
            for follow in follows :
                if follow == "docker":
                    print("push docker execute.")
                    tag = subprocess.run(["git","log","--abbrev-commit","--pretty=oneline"], text=True, capture_output=True)
                    tag = tag.stdout
                    tag = tag[:tag.find(" ")]
                    liveprint_exec(["autogit\push_docker.bat", "ghcr.io/enzoescipy/sticker_grasser:" + tag])
                    
                elif follow == "git" : 
                    print("push git execute.")
                    liveprint_exec(["autogit\push_git.bat"])
                else:
                    print("invalid parameter. \n\n\n")
                    return
        else:
            print("invalid parameter. \n\n\n")
            return

def fronter():
    print("---------------welcome to AUTO_GIT-----------------")
    print("exit : exit process")
    print("commit : commit sth. ")
    print("    commit docker > build docker images. tag will be ghcr.io/enzoescipy/sticker_grasser:pending")
    print("    commit git    > add current changes and commit with msg. will be applied to both main, react repos.")
    print("push : push sth.")
    print("    push docker   > push ghcr.io/enzoescipy/sticker_grasser:pending. tag will be change to latest local git commit hashcode.")
    print("    push git      > push git. will be applied to both main, react repos.")
    print("add : git add to repo and submodules. (only work like <add> , not like <commit docker git add>")
    print("if you put command like <push docker git>, autogit will change the orders to <push git docker>.")

    inputstr = input(": ")

    batfunc(inputstr.split(" "))

while True:
    fronter()

