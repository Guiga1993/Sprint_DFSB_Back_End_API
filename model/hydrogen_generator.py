from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property # Needed for smart calculations
from datetime import datetime
from model.base_class import Base 

class HydrogenGenerator(Base):
    __tablename__ = 'hydrogen_generators'

    id = Column("pk_generator", Integer, primary_key=True) 
    serial_number = Column(String(50), unique=True, nullable=False) 
    acquisition_type = Column(String(20), nullable=False) 
    generator_type = Column(String(50), nullable=False) # Changed from 'type' to avoid conflicts
    
    # FK must be provided during creation
    customer_id = Column(Integer, ForeignKey("customers.pk_customer"), nullable=False)
    customer = relationship("Customer", back_populates="generators")

    # Metrics
    stack_voltage_total = Column(Float) 
    stack_current_density = Column(Float) 
    amount_of_cells = Column(Integer) 
    
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, serial_number: str, acquisition_type: str, generator_type: str, 
                 amount_of_cells: int, stack_voltage_total: float, 
                 stack_current_density: float, customer_id: int): # Added customer_id
        self.serial_number = serial_number
        self.acquisition_type = acquisition_type
        self.generator_type = generator_type
        self.amount_of_cells = amount_of_cells
        self.stack_voltage_total = stack_voltage_total
        self.stack_current_density = stack_current_density
        self.customer_id = customer_id

    # This replaces the need for a database column for 'per_cell'
    @hybrid_property
    def stack_voltage_per_cell(self):
        if self.amount_of_cells and self.amount_of_cells > 0:
            return self.stack_voltage_total / self.amount_of_cells
        return 0.0