from agent import Agent, Handler
import udf_pb2
import sys

# The Agent calls the appropriate methods on the Handler as requests are read off STDIN.
#
# Throwing an exception will cause the Agent to stop and an ErrorResponse to be sent.
# Some *Response objects (like SnapshotResponse) allow for returning their own error within the object itself.
# These types of errors will not stop the Agent and Kapacitor will deal with them appropriately.
#
# The Handler is called from a single thread, meaning methods will not be called concurrently.
#
# To write Points/Batches back to the Agent/Kapacitor use the Agent.write_response method, which is thread safe.
class ${Module}Handler(object):
    def __init__(self, agent):
        self._agent = agent

    def info(self):
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.STREAM
        response.info.provides = udf_pb2.STREAM
        return response

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


if __name__ == '__main__':
        # Create an agent
        agent = Agent()
        h = ${Module}Handler(agent)
        agent.handler = h

        # Anything printed to STDERR from a UDF process gets captured into the Kapacitor logs.
        print >> sys.stderr, "Starting agent for ${Module}"
        agent.start()
        agent.wait()
        print >> sys.stderr, "Agent finished"