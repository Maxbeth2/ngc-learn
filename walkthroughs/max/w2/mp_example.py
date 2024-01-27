from remote_plotter import RemotePlotter
import multiprocessing as mp

if __name__ == "__main__":
    rec, snd = mp.Pipe()

    rp = RemotePlotter(rec)
    rp.start()

    snd.send("thee message")


