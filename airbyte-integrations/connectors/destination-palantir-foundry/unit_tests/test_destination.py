# import unittest
# from mockito import when, mock, unstub
# from destination_palantir_foundry.writer import writer, writer_factory
# from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, ConfiguredAirbyteMessage, AirbyteStream


# class TestDestination(unittest.TestCase):

#     def setUp(self):
#         self.writer = mock(writer.Writer)
#         self.writer_factory = mock(writer_factory.WriterFactory)

#         self.test_catalog = mock(ConfiguredAirbyteCatalog)

#         self.input_message_1 = mock(AirbyteMessage)
#         self.input_message_2 = mock(AirbyteMessage)
#         self.input_messages = [self.input_message_1, self.input_message_2]

#     def tearDown(self):
#         unstub()

#     def test_write_registersAllStreams(self):
