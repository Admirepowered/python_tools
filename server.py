import os
import time
import threading
import main as single

time_interval = 720  # 默认签到间隔时间，单位minute(分钟)


def runingtime():
    return int(time.time())


def control(time_interval, event, detal):
    last_time = runingtime()
    while True:
        now_time = runingtime()
        if now_time > last_time + time_interval * 60:
            last_time = runingtime()

            try:
                single.main()
            except:
                print("start failed")
        if event.is_set():
            print("Stoping threading")
            break
        if (detal.is_set()):
            print("The Next check time is {}s".format(last_time - now_time + time_interval * 60))
        time.sleep(20)


def command(detal):
    global mod
    global time_interval
    global show
    help = "help\n" \
           "info\n" \
           "Tools\n"
    print(help)
    while True:
        command = input()
        if command == "help" or command == "exit" or command == "?" or command == "":
            print(help)
        if command == "stop" or command == "exit":
            print("Stoping Server Plase Wait")
            return False

        if command == "reload":
            return True
        if command == "test":

            try:
                single.main()
            except:
                print("error")

        command = command.split(' ')
        for i in range(0, len(command)):
            if command[i] == "time":
                if len(command) == 2:
                    time_interval = int(command[1])
                    print("switching interval to {} minute".format(time_interval))
                    return True
            if command[i] == "show":
                if len(command) == 2:

                    if command[1] == "true":
                        detal.set()
                        print("switching to detail mod")

                    if command[1] == "false":
                        detal.clear()
                        print("switching to slient mod")


                else:
                    print("Error Command")
    return True


if __name__ == '__main__':
    while True:
        t1_stop = threading.Event()
        detal = threading.Event()
        thread1 = threading.Thread(name='time_check', target=control, args=(time_interval, t1_stop, detal))
        thread1.start()
        try:
            if command(detal):
                t1_stop.set()
                continue
            else:
                t1_stop.set()
                break
        except:
            t1_stop.set()
            continue
