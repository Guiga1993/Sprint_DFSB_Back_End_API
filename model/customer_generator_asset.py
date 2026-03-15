from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from model.base_class import Base


class CustomerGeneratorAsset(Base):
    __tablename__ = 'customer_generator_assets'

    asset_id: Mapped[int] = mapped_column("pk_asset", Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.pk_customer"), nullable=False)
    generator_id: Mapped[int] = mapped_column(Integer, ForeignKey("hydrogen_generators.pk_generator"), nullable=False)
    generaor_qtd: Mapped[int] = mapped_column(Integer, nullable=False)
    installation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    def __init__(
        self,
        customer_id: int,
        generator_id: int,
        generaor_qtd: int,
        installation_date: datetime | None = None,
    ):
        """Cria um vínculo entre Customer e HydrogenGenerator.

        Arguments:
            customer_id: ID do customer vinculado.
            generator_id: ID do gerador vinculado.
            generaor_qtd: quantidade de geradores no vínculo.
            installation_date: data de instalação do vínculo.
        """
        self.customer_id = customer_id
        self.generator_id = generator_id
        self.generaor_qtd = generaor_qtd

        if installation_date:
            self.installation_date = installation_date
