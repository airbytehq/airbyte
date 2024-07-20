from destination_palantir_foundry.writer.writer import Writer


class WriterFactory:
    def create(self) -> Writer:
        ...
