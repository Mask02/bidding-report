def log(msg):

    with open("log.txt","a") as log_f:

        log_f.write(msg)

        