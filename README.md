# SPlusHydPower
## **Overview**

The S+HydPower QGIS Plugin is a powerful tool designed to estimate hydropower generation and evaluate the socioeconomic impact of watershed management measures. It accomplishes this by utilizing hydrological SWAT+ simulated outputs, which serve as the foundation for estimating hydropower generation and the associated impacts. Additionally, the plugin allows users to explore various scenarios based on the functioning and characteristics of the hydropower system.

 
## **Usage**
### **Data Requirements**

Before using the S+HydPower plugin, ensure that you have the following data and parameters available:

### **SWAT+ Data**
1. **Channels Layer:** This is a vector line layer representing different channel segments. It should be provided in Shapefile format and contains Channel IDs.
2. **SWAT+ Output Files:**
* channel_sd_day: This SQLite database contains hydrological variables for run-of-river hydropower plants, with daily data. It should include Channel IDs and flo_out (flow output) values.
* reservoir_day: This SQLite database contains hydrological variables for reservoir-based hydropower plants, with daily data. It should include Reservoir IDs and flo_out (flow output) values.
### Hydropower Stations and Derivation Points
1. **Hydropower Station Location (Reservoir):** A vector point layer that locates reservoir-based hydropower stations. It should be provided in Shapefile format and include Fmac (maximum flow allowed per contract), HF (usable height of fall), and Ftm (technical minimum flow rate) values.
2. **Hydropower Station Location (Run-of-River):** A vector point layer that locates run-of-river hydropower stations. It should be provided in Shapefile format and include Hydropower station IDs, HF (usable height of fall), and Ftm (technical minimum flow rate) values.
3. **Hydropower Derivation Point (Run-of-River):** A vector point layer that locates the derivation points for run-of-river hydropower plants. It should be provided in Shapefile format and include Hydropower station IDs, Fmef (environmental flow rate), and Fmac (maximum flow allowed per contract) values.
### Administrative Limits
1. **Administrative Limits Layer:** A vector polygon layer outlining the limits of the administration (e.g., watershed, municipality, state). It should be provided in Shapefile format and include Admin IDs.

**Note:** The abbreviations used in the data requirements are defined as follows:

* Fmac: Maximum flow allowed per contract (m³/s).
* HF: Usable height of fall (m).
* Ftm: Technical minimum flow rate (m³/s).
* Fmef: Environmental flow rate.
### Plugin Execution
1. After installing the plugin, load the required data layers into your QGIS project.
2. Activate the S+HydPower plugin by navigating to Plugins > S+HydPower > Run S+HydPower.
3. Configure the plugin by specifying the necessary input data layers and parameters.
4. Run the plugin to estimate hydropower generation and evaluate the socioeconomic impact of watershed management measures.
5. Review the results, which can be aggregated by the desired administrative limits (e.g., watershed, municipality, state).
## Contact

For questions, issues, or support, please visit the issues section of this repository, or email xgarcia@icra.cat

## Credits

This plugin uses an icon designed by Freepick from flaticon (https://www.flaticon.com/free-icons/hydro-power).
