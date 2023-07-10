import av


class VideoWriter():

    def __init__(self, dstfile, fps, options={}):
        fps = int(round(fps))
        self.container = av.open(dstfile, mode="w")
        self.stream = self.container.add_stream("h264", rate=fps)
        self.stream.options = options
        self.init = False

    def write(self, frame):
        W, H = frame.shape[:2][::-1]
        if not self.init:
            self.stream.width = W
            self.stream.height = H
            self.init = True

        if self.stream.width != W or self.stream.height != H:
            raise Exception(f"Invalid frame shape: {(W,H)}, required: "
                            f"{(self.stream.width, self.stream.height)}")

        frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        packet = self.stream.encode(frame)
        self.container.mux(packet)

    def close(self):
        self.container.close()
