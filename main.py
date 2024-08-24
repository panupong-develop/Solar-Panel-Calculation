from typing import Literal
import streamlit as st
from dataclasses import dataclass


class WithCalcPower:
    """
    A mixin class providing the `total_power` property 
    to calculate power based on voltage and current.
    """
    voltage: int
    current: int
    
    @property
    def total_power(self) -> int:
        return self.voltage * self.current


@dataclass
class Panel(WithCalcPower):
    """
    Represents an individual solar panel with voltage and current
    """
    voltage: int
    current: int

MergedPanel = Panel
PanelGroup = list[Panel]

@dataclass
class Output(WithCalcPower):
    """
    Represetns the system output
    """
    voltage: int
    current: int
    num_series: int
    num_parallel: int

@dataclass
class Optimized(WithCalcPower):
    """
    Represents the optimal system output
    """
    voltage: int
    current: int
    num_series: int
    num_parallel: int
    loss_power: int



def group_panels(panels: list[Panel], chunk_size: int) -> list[PanelGroup]:
    return [panels[i : i + chunk_size] for i in range(0, len(panels), chunk_size)]


def series_panels(panels: list[Panel]) -> MergedPanel:
    v = sum(panel.voltage for panel in panels)  # sum of voltages
    i = panels[0].current  # current remains the same in series
    return Panel(v, i)


def parallel_panels(panels: list[Panel]) -> MergedPanel:
    v = panels[0].voltage  # voltage remains the same
    i = sum(panel.current for panel in panels)  # sum of current
    return Panel(v, i)


def evaluate(panels: list[Panel], chunk_size: int) -> Output:
    groups = group_panels(panels=panels, chunk_size=chunk_size)
    series = [series_panels(panels) for panels in groups]
    result = parallel_panels(series)
    num_series = chunk_size
    num_parallel = len(series)

    return Output(
        voltage=result.voltage,
        current=result.current,
        num_series=num_series,
        num_parallel=num_parallel,
    )


def optimize(panels, max_voltage, max_current, max_power) -> Optimized | None:
    best_config: Output | None = None
    best_power = 0

    for group_size in range(1, len(panels) + 1):
        output: Output = evaluate(panels, group_size)

        if output.voltage <= max_voltage and output.current <= max_current:
            if output.total_power > best_power:
                best_power = output.total_power
                best_config = output

    # cannot find the optimal point
    if best_config is None:
        return None

    return Optimized(
        voltage=best_config.voltage,
        current=best_config.current,
        num_series=best_config.num_series,
        num_parallel=best_config.num_parallel,
        loss_power=max_power - best_config.total_power
    )


# Streamlit UI
st.title("Optimize Solar Panel Configuration")
st.markdown("Finds the best series-parallel combination to maximize power output while staying within the user-defined system constraints.")
st.subheader("Enter System Constraints")
max_voltage = st.number_input("Max System Voltage (V)", min_value=1, step=1, value=50)
max_current = st.number_input("Max System Current (A)", min_value=1, step=1, value=30)
max_power = st.number_input("Max System Power (W)", min_value=1, step=1, value=500)

st.subheader("Enter Panel Specifications")
panel_voltage = st.number_input("Panel Voltage (V)", min_value=1, step=1, value=18)
panel_current = st.number_input("Panel Current (A)", min_value=1, step=1, value=8)
total_panels = st.number_input("Total Number of Panels", min_value=1, step=1, value=6)

panels = [Panel(panel_voltage, panel_current)] * total_panels

if st.button("Optimize Configuration"):
    best_config = optimize(panels, max_voltage, max_current, max_power)

    if best_config is None:
        st.write("No valid configuration found within the constraints.")
    
    else:
        st.write(f"**Best Configuration Found:**")
        st.write(f"Series: {best_config.num_series}/group ->  Parellel: {best_config.num_parallel}")
        st.write(f"- Total Voltage: {best_config.voltage} V")
        st.write(f"- Total Current: {best_config.current} A")
        st.write(f"- Total Power: {best_config.total_power} W")
        st.write(f"- Loss Power: {best_config.loss_power} W")
