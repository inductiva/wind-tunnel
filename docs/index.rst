Wind Tunnel Package
===================

The **Wind Tunnel** package via Inductiva API allows users to set up and run virtual wind tunnel simulations easily. It leverages the **OpenFOAM** simulator for computational fluid dynamics and provides an interface for configuring simulation scenarios, running simulations, and processing results.

**Features:**
   - Simplifies simulation workflow for vehicle aerodynamics.
   - Configures OpenFOAM simulation files with specified parameters.
   - Provides scripts for running standalone and batch simulations.
   - Supports running simulations on dedicated hardware.

**Quick Start Guide:**

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/inductiva/wind-tunnel.git
      cd wind-tunnel

2. Install the package:

   .. code-block:: bash

      pip install .

3. Run simulations using provided scripts or create your own.


.. toctree::
   :maxdepth: 5
   :caption: Table of Contents
   :name: mastertoc

   windtunnel.windtunnel
   windtunnel.windtunnel_outputs
   windtunnel.display
   windtunnel.pre_processing
   windtunnel.utils
