# The Agent calls the appropriate methods on the Handler as requests are read off STDIN.
#
# Throwing an exception will cause the Agent to stop and an ErrorResponse to be sent.
# Some *Response objects (like SnapshotResponse) allow for returning their own error within the object itself.
# These types of errors will not stop the Agent and Kapacitor will deal with them appropriately.
#
# The Handler is called from a single thread, meaning methods will not be called concurrently.
#
# To write Points/Batches back to the Agent/Kapacitor use the Agent.write_response method, which is thread safe.
class ${module}Handler(object):
    def info(self):
        pass
    def init(self, init_req):
        pass
    def snapshot(self):
        pass
    def restore(self, restore_req):
        pass
    def begin_batch(self, begin_req):
        pass
    def point(self, point):
        pass
    def end_batch(self, end_req):
        pass