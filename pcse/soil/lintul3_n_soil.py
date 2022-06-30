from pcse.traitlets import Float
from pcse.decorators import prepare_rates, prepare_states
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject
from pcse import signals

class Lintul3_N_Soil_PotentialProduction(SimulationObject):
    """Provides unlimited soil N/ for potential production simulations.

    NAVAIL just remain 100 kg/ha whatever the crop takes.
    """

    class StateVariables(StatesTemplate):
        TNSOIL = Float(-99.)  # total mineral N from soil and fertiliser  g N ha-1

    def initialize(self, day, kiosk, parvalues):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs
        """
        self.states = self.StateVariables(kiosk, publish=["TNSOIL"], TNSOIL=100.)

    def calc_rates(self, day, drv):
        pass

    @prepare_states
    def integrate(self, day, delt=1.0):
        self.touch()

class Lintul3_N_Soil(SimulationObject):
    FERTNS = 0.

    class StateVariables(StatesTemplate):
        TNSOIL = Float(-99.)  # total mineral N from soil and fertiliser  kg N ha-1

    class Parameters(ParamTemplate):
        RNMIN = Float(-99.)

    class RateVariables(RatesTemplate):
        RNSOIL2 = Float(-99.)

    def initialize(self, day, kiosk, parvalues):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs
        """
        self.states = self.StateVariables(kiosk, publish=["TNSOIL"], TNSOIL=0.)
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk)
        self.kiosk = kiosk
        self._connect_signal(self._on_APPLY_N, signals.apply_n)


    @prepare_rates
    def calc_rates(self, day, drv):
        r = self.rates
        s = self.states
        p = self.params
        k = self.kiosk

        DELT = 1.
        r.RNSOIL2 = self.FERTNS/DELT - k.NUPTR + p.RNMIN
        self.FERTNS = 0.0

    @prepare_states
    def integrate(self, day, delt=1.0):
        rates = self.rates
        states = self.states

        # mineral N amount in the soil
        states.TNSOIL += rates.RNSOIL2

    def _on_APPLY_N(self, amount, recovery):
        """Receive signal for N application with amount the nitrogen amount in g N m-2 and
        recovery the recovery fraction.
        """
        self.FERTNS = amount * recovery